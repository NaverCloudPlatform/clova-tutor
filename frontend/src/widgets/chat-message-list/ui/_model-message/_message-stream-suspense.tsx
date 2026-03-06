/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { isMatching } from 'ts-pattern';
import { useGetChatsByChatIdMessagesSuspenseQuery } from '@/entities/chats/api/queries';

import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import type { ChatMessageProps } from '../../types/chats';

type MessageStreamSuspenseProps = {
  fallback: React.ReactNode;
} & Omit<ChatMessageProps, 'messageId'> &
  React.PropsWithChildren;

export function MessasgeStreamSuspense({
  messageIndex,
  isLastMessage,
  fallback,
  children,
}: MessageStreamSuspenseProps) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: message } = useGetChatsByChatIdMessagesSuspenseQuery(
    {
      chatId: Number(chatId),
    },
    {
      select: (data) => {
        return data.data.at(messageIndex);
      },
    },
  );
  const { isStreaming } = useChatStreamMutationState({
    chatId: Number(chatId),
  });

  // http-stream이 맺어졌지만, 텍스트가 도착하지 않은 경우에도 로딩을 보여줘야 하기 때문에 텍스트 존재 여부까지 확인합니다.
  const isLoadingChat =
    isStreaming && isLastMessage && isMatching({ contents: [{ m_type: 'text', value: { text: '' } }] })(message);

  if (isLoadingChat) {
    return fallback;
  }

  return children;
}
