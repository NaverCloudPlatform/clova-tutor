/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ChatMessageCreateRequestBodyDto } from '@/shared/api/__generated__/dto';
import type { ChatsByChatIdMessagesStreamCallbacks } from '../api/stream-handlers';

export interface UseChatStreamMutationCallbacks extends ChatsByChatIdMessagesStreamCallbacks {
  message_send?: () => void;
}

export type StreamMutationParams = {
  chatId: number;
  payload: ChatMessageCreateRequestBodyDto;
  callbacks?: UseChatStreamMutationCallbacks;
  abortController?: AbortController;
};
