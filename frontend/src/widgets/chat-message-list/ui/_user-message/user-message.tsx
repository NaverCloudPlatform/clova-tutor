/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { UserMessageRetryWrapper } from '@/features/message-actions/ui/user-message-retry-wrapper';
import type { ChatMessageProps } from '../../types/chats';
import { MessageContent } from './_message-content';

type UserMessageProps = Omit<ChatMessageProps, 'messageId'>;

export function UserMessage({ messageIndex, isLastMessage }: UserMessageProps) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { isStreaming, status } = useChatStreamMutationState({
    chatId: Number(chatId),
  });

  if (!isStreaming && isLastMessage && status === 'error') {
    return (
      <UserMessageRetryWrapper>
        <MessageContent messageIndex={messageIndex} />
      </UserMessageRetryWrapper>
    );
  }

  return <MessageContent messageIndex={messageIndex} />;
}
