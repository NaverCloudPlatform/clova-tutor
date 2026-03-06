/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import { ReadableStreamHandler, StreamHandlerError } from '@/shared/api/__generated__/stream-utils';
import { isChatMessageResponseDto } from '@/shared/api/__generated__/type-guards';
import { isMessageDeltaData } from '../type-guards/stream';

export type ChatsByChatIdMessagesStreamCallbacks = {
  message_start?: (data: ChatMessageResponseDto) => void;
  message_delta?: (data: { text: string }) => void;
  message_end?: (data: ChatMessageResponseDto) => void;
  error?: (error: ({ type: 'stream-handler-error' } & StreamHandlerError) | unknown) => void;
};

export class ChatsByChatIdMessagesStreamHandler extends ReadableStreamHandler {
  constructor(response: Response, callbacks: ChatsByChatIdMessagesStreamCallbacks) {
    super(
      response,
      {
        message_start: (data) => {
          if (isChatMessageResponseDto(data)) {
            callbacks.message_start?.(data);
          }
        },
        message_delta: (data) => {
          if (isMessageDeltaData(data)) {
            callbacks.message_delta?.(data);
          }
        },
        message_end: (data) => {
          if (isChatMessageResponseDto(data)) {
            callbacks.message_end?.(data);
          }
        },
        error: (error) => {
          if (error instanceof StreamHandlerError) {
            callbacks.error?.({ type: 'stream-handler-error', ...error });
            return;
          }

          callbacks.error?.(error);
        },
      },
      {
        completionEventType: 'message_end',
      },
    );
  }
}

export type ChatsByChatIdResumeStreamCallbacks = ChatsByChatIdMessagesStreamCallbacks;
export class ChatsByChatIdResumeStreamHandler extends ChatsByChatIdMessagesStreamHandler {}
