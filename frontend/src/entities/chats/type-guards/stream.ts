/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ChatsByChatIdMessagesStreamCallbacks } from '../api/stream-handlers';
import { messageDeltaDataSchema } from '../schema/stream';

export const isMessageDeltaData = (data: unknown): data is { text: string } => {
  return messageDeltaDataSchema.safeParse(data).success;
};

export const isStreamCallbacks = (data: unknown): data is ChatsByChatIdMessagesStreamCallbacks => {
  if (typeof data !== 'object' || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;

  return (
    (typeof obj.message_start === 'function' || typeof obj.message_start === 'undefined') &&
    (typeof obj.message_delta === 'function' || typeof obj.message_delta === 'undefined') &&
    (typeof obj.message_end === 'function' || typeof obj.message_end === 'undefined') &&
    (typeof obj.error === 'function' || typeof obj.error === 'undefined')
  );
};
