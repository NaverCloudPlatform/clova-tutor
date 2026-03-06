/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { randomUUID } from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import type { NetworkLogV1_1, StreamChunk } from '../mocks/types/network-log';

// API 경로 패턴 (환경에 관계없이 이 경로로 시작하는 요청만 필터링)
const API_PATH_PREFIX = '/api/v1';

const HEADER_POLICY = {
  whitelist: ['content-type', 'accept', 'x-user-id', 'cache-control'],
  blacklist: ['authorization', 'cookie', 'set-cookie'],
};

const DEFAULT_INPUT_DIR = './mocks/__data__/network-logs';

async function main() {
  const inputDir = process.argv[2] || DEFAULT_INPUT_DIR;

  console.info(`[har-to-network-log] 디렉터리 스캔 중: ${inputDir}`);

  try {
    await fs.access(inputDir);
  } catch {
    console.error(`[har-to-network-log] 디렉터리를 찾을 수 없습니다: ${inputDir}`);
    process.exit(1);
  }

  const files = await fs.readdir(inputDir);
  const harFiles = files.filter((file) => file.endsWith('.har'));

  if (harFiles.length === 0) {
    console.warn(`[har-to-network-log] .har 파일을 찾을 수 없습니다.`);
    return;
  }

  console.info(`[har-to-network-log] ${harFiles.length}개의 .har 파일 발견`);

  let totalConverted = 0;

  for (const harFile of harFiles) {
    const harPath = path.join(inputDir, harFile);
    const outputFileName = harFile.replace('.har', '.json');
    const outputPath = path.join(inputDir, outputFileName);

    try {
      const harText = await fs.readFile(harPath, 'utf-8');
      const har = JSON.parse(harText);

      const records: NetworkLogV1_1[] = har.log.entries
        .filter((entry: any) => {
          try {
            const url = new URL(entry.request.url);
            return url.pathname.startsWith(API_PATH_PREFIX);
          } catch {
            return false;
          }
        })
        .map((entry: any) => convertEntry(entry));

      await fs.writeFile(outputPath, JSON.stringify(records, null, 2));

      // 변환 성공 시 원본 .har 파일 삭제
      await fs.unlink(harPath);

      console.info(
        `  ✓ ${harFile} → ${outputFileName} (${records.length} records) [원본 삭제됨]`,
      );
      totalConverted++;
    } catch (error) {
      console.error(`  ✗ ${harFile} 변환 실패:`, error);
    }
  }

  console.info(
    `\n[har-to-network-log] 완료: ${totalConverted}/${harFiles.length} 파일 변환됨`,
  );
}

function convertEntry(entry: any): NetworkLogV1_1 {
  const requestTs = new Date(entry.startedDateTime).getTime();
  const responseTs = requestTs + Math.round(entry.time ?? 0);

  const requestHeaders = filterHeaders(
    Object.fromEntries(entry.request.headers.map((h: any) => [h.name, h.value])),
    HEADER_POLICY,
  );

  const responseHeaders = filterHeaders(
    Object.fromEntries(entry.response.headers.map((h: any) => [h.name, h.value])),
    HEADER_POLICY,
  );

  // URL에서 pathname + search만 추출 (호스트 제거)
  const urlPath = extractPathFromUrl(entry.request.url);

  const mimeType = entry.response.content?.mimeType;
  const rawText = decodeResponseBody(entry.response.content);

  if (mimeType === 'text/event-stream') {
    const streamBody = parseEventStream(rawText);

    return {
      id: randomUUID(),
      version: '1.1',
      request: {
        method: entry.request.method,
        url: urlPath,
        headers: requestHeaders,
        payload: entry.request.postData?.text
          ? safeJsonParse(entry.request.postData.text)
          : undefined,
        timestamp: requestTs,
      },
      response: {
        mode: 'event-stream',
        status: entry.response.status,
        statusText: entry.response.statusText,
        headers: responseHeaders,
        body: streamBody,
        timestamp: responseTs,
      },
      totalDuration: entry.time,
    };
  }

  return {
    id: randomUUID(),
    version: '1.1',
    request: {
      method: entry.request.method,
      url: urlPath,
      headers: requestHeaders,
      payload: entry.request.postData?.text
        ? safeJsonParse(entry.request.postData.text)
        : undefined,
      timestamp: requestTs,
    },
    response: {
      mode: 'single',
      status: entry.response.status,
      statusText: entry.response.statusText,
      headers: responseHeaders,
      body: safeJsonParse(rawText),
      timestamp: responseTs,
    },
    totalDuration: entry.time,
  };
}


/**
 * URL에서 pathname + search 부분만 추출 (호스트 제거)
 * 예: http://localhost:8000/api/v1/users?page=1 → /api/v1/users?page=1
 */
function extractPathFromUrl(fullUrl: string): string {
  try {
    const url = new URL(fullUrl);
    return url.pathname + url.search;
  } catch {
    // URL 파싱 실패 시 원본 반환
    return fullUrl;
  }
}

function decodeResponseBody(content: any): string {
  if (!content?.text) return '';
  if (content.encoding === 'base64') {
    return Buffer.from(content.text, 'base64').toString('utf-8');
  }
  return content.text;
}

function parseEventStream(text: string): StreamChunk[] {
  const chunks: StreamChunk[] = [];

  const blocks = text.split('\n\n').filter(Boolean);

  for (const block of blocks) {
    let event: StreamChunk['event'] | undefined;
    let data: unknown;

    for (const line of block.split('\n')) {
      if (line.startsWith('event:')) {
        event = line.replace('event:', '').trim() as StreamChunk['event'];
      }
      if (line.startsWith('data:')) {
        data = safeJsonParse(line.replace('data:', '').trim());
      }
    }

    if (event) {
      chunks.push({ event, data });
    }
  }

  return chunks;
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function filterHeaders(
  headers: Record<string, string>,
  policy: { whitelist?: string[]; blacklist?: string[] },
) {
  const lower = (s: string) => s.toLowerCase();
  let entries = Object.entries(headers);

  if (policy.whitelist?.length) {
    const wl = policy.whitelist.map(lower);
    entries = entries.filter(([k]) => wl.includes(lower(k)));
  }

  if (policy.blacklist?.length) {
    const bl = policy.blacklist.map(lower);
    entries = entries.filter(([k]) => !bl.includes(lower(k)));
  }

  return Object.fromEntries(entries);
}

main().catch(console.error);