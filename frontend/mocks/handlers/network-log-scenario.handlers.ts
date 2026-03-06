/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { RequestHandler } from 'msw';
import { HttpResponse, http } from 'msw';
import type { NetworkLogV1_1 } from '../types/network-log';
import { log } from '@/shared/core/log';

/**
 * MSW를 위한 API 호스트 URL
 * 환경변수 VITE_API_BASE_URL에서 호스트 부분만 추출
 */
const getApiHostUrl = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL as string;
  const url = new URL(apiBaseUrl);
  return `${url.protocol}//${url.host}`;
};

const SCENARIO_JSON_MAP = {
  'TC-1.1': () => import('../__data__/network-logs/tc-1.1.json').then((m) => m.default),
  'TC-1.2': () => import('../__data__/network-logs/tc-1.2.json').then((m) => m.default),
  'TC-1.4': () => import('../__data__/network-logs/tc-1.4.json').then((m) => m.default),
  'TC-1.5': () => import('../__data__/network-logs/tc-1.5.json').then((m) => m.default),
  'TC-1.6': () => import('../__data__/network-logs/tc-1.6.json').then((m) => m.default),
  'TC-1.7': () => import('../__data__/network-logs/tc-1.7.json').then((m) => m.default),
  'TC-2.2': () => import('../__data__/network-logs/tc-2.2.json').then((m) => m.default),
  'TC-3.1': () => import('../__data__/network-logs/tc-3.1.json').then((m) => m.default),
  'TC-3.2': () => import('../__data__/network-logs/tc-3.2.json').then((m) => m.default),
  'TC-3.3': () => import('../__data__/network-logs/tc-3.3.json').then((m) => m.default),
  'TC-3.4.1': () => import('../__data__/network-logs/tc-3.4.1.json').then((m) => m.default),
  'TC-3.4.3': () => import('../__data__/network-logs/tc-3.4.3.json').then((m) => m.default),
  'TC-3.5': () => import('../__data__/network-logs/tc-3.5.json').then((m) => m.default),
  'TC-3.6': () => import('../__data__/network-logs/tc-3.6.json').then((m) => m.default),
  'TC-4.1': () => import('../__data__/network-logs/tc-4.1.json').then((m) => m.default),
  'TC-4.2': () => import('../__data__/network-logs/tc-4.2.json').then((m) => m.default),
  'TC-4.4': () => import('../__data__/network-logs/tc-4.4.json').then((m) => m.default),
  'TC-4.5.9': () => import('../__data__/network-logs/tc-4.5.9.json').then((m) => m.default),
  'TC-4.5.11': () => import('../__data__/network-logs/tc-4.5.11.json').then((m) => m.default),
  'TC-4.6': () => import('../__data__/network-logs/tc-4.6.json').then((m) => m.default),
  'TC-4.7': () => import('../__data__/network-logs/tc-4.7.json').then((m) => m.default),
  'TC-5.1': () => import('../__data__/network-logs/tc-5.1.json').then((m) => m.default),
  'TC-5.2': () => import('../__data__/network-logs/tc-5.2.json').then((m) => m.default),
  'TC-5.3': () => import('../__data__/network-logs/tc-5.3.json').then((m) => m.default),
  'TC-6.1': () => import('../__data__/network-logs/tc-6.1.json').then((m) => m.default),
  'TC-6.2': () => import('../__data__/network-logs/tc-6.2.json').then((m) => m.default),
  'TC-6.3': () => import('../__data__/network-logs/tc-6.3.json').then((m) => m.default),
  'TC-7.1': () => import('../__data__/network-logs/tc-7.1.json').then((m) => m.default),
  'TC-7.2': () => import('../__data__/network-logs/tc-7.2.json').then((m) => m.default),
  'TC-7.3': () => import('../__data__/network-logs/tc-7.3.json').then((m) => m.default),
  'TC-7.4': () => import('../__data__/network-logs/tc-7.4.json').then((m) => m.default),
  'TC-7.5': () => import('../__data__/network-logs/tc-7.5.json').then((m) => m.default),
  'TC-7.7': () => import('../__data__/network-logs/tc-7.7.json').then((m) => m.default),
  'TC-8.1': () => import('../__data__/network-logs/tc-8.1.json').then((m) => m.default),
  'TC-8.3': () => import('../__data__/network-logs/tc-8.3.json').then((m) => m.default),
  'TC-8.4': () => import('../__data__/network-logs/tc-8.4.json').then((m) => m.default),
  'TC-8.5': () => import('../__data__/network-logs/tc-8.5.json').then((m) => m.default),
  'TC-8.7': () => import('../__data__/network-logs/tc-8.7.json').then((m) => m.default),
  'chat-send-error': () => import('../__data__/network-logs/chat-send-error.json').then((m) => m.default),
  'chat-stream-eof-error': () => import('../__data__/network-logs/chat-stream-eof-error.json').then((m) => m.default),
};

/**
 * 시나리오 ID에 해당하는 핸들러를 로드
 * @param scenarioId - 시나리오 ID (예: 'TC-4.6', 'demo_math_1')
 * @returns MSW 핸들러 배열
 */
export async function loadScenarioHandlers(scenarioId: string): Promise<RequestHandler[]> {
  const handlers = [];

  const loader = SCENARIO_JSON_MAP[scenarioId as keyof typeof SCENARIO_JSON_MAP];
  if (!loader) {
    console.warn(`[MSW] 시나리오를 찾을 수 없습니다: ${scenarioId}`);
    return [];
  }

  try {
    const networkLogs = (await loader()) as unknown as NetworkLogV1_1[];
    const endpointGroups = groupRecordsByEndpoint(networkLogs);
    const apiHostUrl = getApiHostUrl();

    log.info('[MSW] API Host URL:', apiHostUrl);
    log.info('[MSW] Endpoint Groups:', endpointGroups);

    for (const [key, records] of endpointGroups.entries()) {
      const [method, pathname] = key.split('::');
      const httpMethod = method.toLowerCase();

      if (!isHttpMethod(httpMethod)) {
        continue;
      }

      // 전체 URL (API 또는 외부 URL)
      const fullUrl = isExternalUrl(pathname) ? pathname : apiHostUrl + pathname;

      let callCount = 0;

      const handler = http[httpMethod](fullUrl, () => {
        callCount++;
        const responseIndex = Math.min(callCount - 1, records.length - 1);
        const record = records[responseIndex];
        const xCallCount = `${callCount.toString()}/${records.length}`;

        if (record.response.mode === 'single') {
          return new HttpResponse(JSON.stringify(record.response.body), {
            status: record.response.status,
            statusText: record.response.statusText,
            headers: {
              ...record.response.headers,
              'x-call-count': xCallCount,
            },
          });
        }

        if (record.response.mode === 'event-stream') {
          const stream = createStreamingResponse(record);
          return new HttpResponse(stream, {
            status: record.response.status,
            headers: {
              'Content-Type': 'text/event-stream',
              'Cache-Control': 'no-cache',
              Connection: 'keep-alive',
              'x-call-count': xCallCount,
            },
          });
        }

        return new HttpResponse(null, { status: 200 });
      });

      handlers.push(handler);
    }

    console.info(`[MSW] 시나리오 로드 완료: ${scenarioId} (${endpointGroups.size}개 핸들러)`);

    return handlers;
  } catch (error) {
    console.error(`[MSW] 시나리오 로드 실패: ${scenarioId}`, error);
    return [];
  }
}

/**
 * 시나리오 ID가 유효한지 확인
 */
export function isValidScenario(scenarioId: string): boolean {
  return scenarioId in SCENARIO_JSON_MAP;
}

/**
 * HTTP 메서드가 유효한지 확인
 */
function isHttpMethod(method: string): method is keyof typeof http {
  return method in http;
}

/**
 * 외부 URL인지 확인 (http:// 또는 https://로 시작)
 */
function isExternalUrl(url: string): boolean {
  return url.startsWith('http://') || url.startsWith('https://');
}

/**
 * 요청 URL과 메서드를 기준으로 핸들러를 그룹화
 * URL은 경로만 포함 (예: /api/v1/users?page=1)
 * 실제 핸들러 등록 시 BASE_URL이 앞에 붙음
 */
function groupRecordsByEndpoint(networkLogs: NetworkLogV1_1[]) {
  const endpointGroups = new Map<string, NetworkLogV1_1[]>();

  for (const networkLog of networkLogs) {
    const key = `${networkLog.request.method}::${networkLog.request.url}`;
    
    if (!endpointGroups.has(key)) {
      endpointGroups.set(key, []);
    }

    endpointGroups.get(key)?.push(networkLog);
  }

  return endpointGroups;
}

/**
 * 스트리밍 응답 생성
 */
function createStreamingResponse(networkLog: NetworkLogV1_1) {
  const encoder = new TextEncoder();

  return new ReadableStream({
    async start(controller) {
      if (networkLog.response.mode !== 'event-stream') {
        controller.close();
        return;
      }

      // 첫 스트림 시작까지 1초 대기
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const streamChunks = networkLog.response.body;

      for (const chunk of streamChunks) {
        // delay가 있으면 대기
        if (chunk.delay) {
          await new Promise((resolve) => setTimeout(resolve, chunk.delay));
        }

        // SSE 형식으로 인코딩
        const eventType = chunk.event;
        const eventData = typeof chunk.data === 'string' ? chunk.data : JSON.stringify(chunk.data);

        controller.enqueue(encoder.encode(`event: ${eventType}\ndata: ${eventData}\n\n`));
      }

      controller.close();
    },
  });
}
