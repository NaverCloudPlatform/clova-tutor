/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import React from 'react';
import { match } from 'ts-pattern';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { ChatImages } from '@/entities/chats/ui/chat-images';
import { ModelStreamingTextMessage } from '@/entities/chats/ui/model-message/model-stream-text-message';
import { ModelTextMessage } from '@/entities/chats/ui/model-message/model-text-message';
import { sortMessageContents } from '@/entities/chats/utils/message-content';
import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import type { ChatMessageProps } from '../../types/chats';
import { MessageProblemRecommended } from './_message-problem-recommended';

type MessageContentsProps = {
  messageId?: ChatMessageResponseDto['id'];
  chatContents: ChatMessageResponseDto['contents'];
} & Pick<ChatMessageProps, 'isLastMessage'>;

export function MessageContents({ messageId, chatContents, isLastMessage }: MessageContentsProps) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { isStreaming } = useChatStreamMutationState({
    chatId: Number(chatId),
  });
  const sortedContents = sortMessageContents(chatContents);

  const handleCopy = async () => {
    await navigator.clipboard.readText();
  };

  return (
    <div className="flex flex-col gap-y-2" onCopy={handleCopy}>
      {sortedContents.map((content, index) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: 순서 변경될 일 없음
        <React.Fragment key={content.m_type + content.value.toString() + index}>
          {match(content)
            .with({ m_type: 'images' }, (content) => (
              <div className="mb-2 self-start">
                <ChatImages images={content.value.sources} />
              </div>
            ))
            .with({ m_type: 'text' }, (content) =>
              isLastMessage && isStreaming ? (
                <ModelStreamingTextMessage content={content} messageId={messageId} />
              ) : (
                <ModelTextMessage content={content} messageId={messageId} />
              ),
            )
            .with({ m_type: 'problem_recommended' }, (content) => (
              <MessageProblemRecommended content={content.value} isLastMessage={isLastMessage} messageId={messageId} />
            ))
            .otherwise(() => null)}
        </React.Fragment>
      ))}
    </div>
  );
}
