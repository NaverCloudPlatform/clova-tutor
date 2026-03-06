/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams, useSearch } from '@tanstack/react-router';
import { useGetChatsByChatIdMessagesSuspenseQuery } from '@/entities/chats/api/queries';
import { ModelMessageBadge } from '@/entities/chats/ui/model-message';
import type { ChatMessageProps } from '../../types/chats';

type MessageBadgeProps = {
  className?: string;
} & Pick<ChatMessageProps, 'messageIndex'>;

export function MessageBadge({ className, messageIndex }: MessageBadgeProps) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { dev } = useSearch({ from: '/_student/$subject/chats/$chat_id' });
  const { data: chatMetadata } = useGetChatsByChatIdMessagesSuspenseQuery(
    {
      chatId: Number(chatId),
    },
    {
      select: (data) => {
        const message = data.data.at(messageIndex);

        return message?.metadata;
      },
    },
  );

  return <ModelMessageBadge className={className} dev={dev} messageMetadata={chatMetadata} />;
}
