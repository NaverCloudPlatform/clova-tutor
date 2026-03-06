/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export type HttpMethod =
  | 'GET'
  | 'POST'
  | 'PUT'
  | 'PATCH'
  | 'DELETE'
  | 'OPTIONS'
  | 'HEAD';

export type StreamChunk = {
  event: 'message_start' | 'message_delta' | 'message_end';
  data: unknown;
  delay?: number;
};

export type NetworkLogV1_1 = {
  id: string;
  version: '1.1';

  request: {
    method: HttpMethod;
    url: string;
    headers: Record<string, string>;
    query?: Record<string, string | string[]>;
    payload?: unknown;
    timestamp: number;
  };

  response: {
    status: number;
    statusText?: string;
    headers: Record<string, string>;
    timestamp: number;
  } & (
    | { mode: 'single'; body: unknown }
    | { mode: 'event-stream'; body: StreamChunk[] }
  );

  totalDuration?: number;
};