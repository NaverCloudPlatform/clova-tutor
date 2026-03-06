/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import React from 'react';
import { match } from 'ts-pattern';
import { useGetChatsByChatIdMessagesSuspenseQuery } from '@/entities/chats/api/queries';

import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { cn } from '@/shared/utils/utils';
import type { ChatMessageProps } from '../types/chats';
import { ModelMessage } from './_model-message';
import { SystemMessage } from './_system-message';
import { UserChat } from './_user-message';

export function ChatMessage({ messageIndex, isLastMessage }: ChatMessageProps) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: message } = useGetChatsByChatIdMessagesSuspenseQuery(
    {
      chatId: Number(chatId),
    },
    {
      select: (data) => {
        const message = data.data.at(messageIndex);

        return {
          type: message?.type,
          author: message?.author,
        };
      },
    },
  );
  const { isStreaming } = useChatStreamMutationState({
    chatId: Number(chatId),
  });

  if (!message) return null;

  return (
    <React.Fragment>
      {match(message)
        .with({ type: 'chat', author: { role: 'user' } }, () => (
          <article className={cn(isStreaming && 'last:min-h-[calc(100dvh-218px)]', 'flex flex-col group')}>
            <UserChat messageIndex={messageIndex} isLastMessage={isLastMessage} />
          </article>
        ))
        .with({ type: 'chat', author: { role: 'assistant' } }, () => (
          <article className="last:min-h-[calc(100dvh-282px)] group">
            <ModelMessage messageIndex={messageIndex} isLastMessage={isLastMessage} />
          </article>
        ))
        .with({ type: 'system' }, () => <SystemMessage messageIndex={messageIndex} />)
        .otherwise(() => null)}
    </React.Fragment>
  );
}
