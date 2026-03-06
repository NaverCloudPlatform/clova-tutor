/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { useEffect, useRef } from 'react';
import { useGetChatsByChatIdMessagesSuspenseQuery } from '@/entities/chats/api/queries';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';

import { useBottomScrollContext } from '@/shared/ui/bottom-scroll-area';
import { Skeleton } from '@/shared/ui/skeleton';
import { ChatMessage } from './_chat-message';

export function ChatMessageList() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { scrollToBottom } = useBottomScrollContext();
  const scrollToBottomRef = useRef(scrollToBottom);
  const prevChatIdRef = useRef<string | null>(null);
  const { context } = useChatStreamMutationState({ chatId: Number(chatId) });
  const { data: messageList } = useGetChatsByChatIdMessagesSuspenseQuery(
    {
      chatId: Number(chatId),
    },
    {
      select: (data) => {
        return data.data.map((message, index) => ({
          id: message.id,
          stableKey: `${chatId}-${index}`,
        }));
      },
    },
  );

  // scrollToBottom 함수의 최신 참조 유지
  useEffect(() => {
    scrollToBottomRef.current = scrollToBottom;
  }, [scrollToBottom]);

  // 기존 채팅방 진입 시에만 맨 아래로 스크롤 (채팅 생성 후 이동 시에는 스크롤하지 않음)
  useEffect(() => {
    // 같은 chatId면 스크롤하지 않음 (Suspense 리마운트 방지)
    if (prevChatIdRef.current === chatId) return;
    prevChatIdRef.current = chatId;

    // 채팅 생성 후 이동한 경우 스크롤하지 않음
    if (context?.isCreateChat) return;

    requestAnimationFrame(() => {
      scrollToBottomRef.current({ smooth: false });

      requestAnimationFrame(() => {
        scrollToBottomRef.current({ smooth: false });
      });
    });
  }, [chatId, context?.isCreateChat]);

  return (
    <section className="flex flex-col w-full" aria-label="채팅 메시지 목록">
      {messageList.map((message, index) => {
        const isLastMessage = index === messageList.length - 1;

        return (
          <ChatMessage
            key={message.stableKey}
            messageId={message.id}
            messageIndex={index}
            isLastMessage={isLastMessage}
          />
        );
      })}
    </section>
  );
}

export function ChatMessageListSkeleton() {
  return (
    <div className="flex flex-col space-y-4 w-full">
      <Skeleton className="h-12 w-3/4 max-w-75 rounded-xl self-end" />

      <Skeleton className="h-40 w-full max-w-130 rounded-xl" />

      <Skeleton className="h-10 w-2/3 max-w-75 rounded-xl self-end" />

      <Skeleton className="h-30 w-full max-w-150 rounded-xl" />
    </div>
  );
}
