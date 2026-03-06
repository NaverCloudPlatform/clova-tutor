/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';

export type ChatMeta = {
  isLastMessage: boolean;
} & Partial<ReturnType<typeof useChatStreamMutationState>>;

export type ChatMessageProps = {
  messageId: number;
  messageIndex: number;
  isLastMessage: boolean;
};
