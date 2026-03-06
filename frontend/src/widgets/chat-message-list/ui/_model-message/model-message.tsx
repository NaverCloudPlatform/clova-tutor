/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';

import { useGetChatsByChatIdMessagesSuspenseQuery } from '@/entities/chats/api/queries';

import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { StreamErrorCallout } from '@/features/message-actions/ui/stream-error-callout';
import type { ChatMessageProps } from '../../types/chats';
import { MessageBadge } from './_message-badge';
import { MessageContents } from './_message-contents';
import { MessageLoadingText } from './_message-loading-text';
import { MessageMenuList } from './_message-menu-list';
import { MessageMetadata } from './_message-metadata';
import { MessasgeStreamSuspense } from './_message-stream-suspense';

type Props = Omit<ChatMessageProps, 'messageId'>;

export function ModelMessage({ messageIndex, isLastMessage }: Props) {
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

        return message?.type === 'chat' ? message : null;
      },
    },
  );
  const { isStreaming, status } = useChatStreamMutationState({
    chatId: Number(chatId),
  });

  if (!message) return null;

  return (
    <div className="pt-6">
      <MessasgeStreamSuspense
        messageIndex={messageIndex}
        isLastMessage={isLastMessage}
        fallback={<MessageLoadingText className="my-2" />}
      >
        <MessageBadge className="h-6" messageIndex={messageIndex} />
        <MessageContents messageId={message.id} chatContents={message.contents} isLastMessage={isLastMessage} />

        {!isStreaming && isLastMessage && status === 'error' && <StreamErrorCallout />}

        {!(isStreaming && isLastMessage) && (
          <div className="space-y-6 animate-in fade-in-0 duration-500 slide-in-from-bottom-2">
            <MessageMenuList message={message} isLastMessage={isLastMessage} />
            <MessageMetadata message={message} isLastMessage={isLastMessage} />
          </div>
        )}
      </MessasgeStreamSuspense>
    </div>
  );
}
