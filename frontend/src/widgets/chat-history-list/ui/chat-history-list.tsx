/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useGetChatsInfiniteSuspenseQuery } from '@/entities/chats/api/queries/use-get-chats-infinity-query';
import type { SubjectEnumDto } from '@/shared/api/__generated__/dto';
import { useInfiniteScroll } from '@/shared/hooks/use-infinite-scroll';
import { Skeleton } from '@/shared/ui/skeleton';
import { ChatListCard } from './chat-list-card';

type ChatHistoryListProps = {
  subject: SubjectEnumDto;
};

export function ChatHistoryList({ subject }: ChatHistoryListProps) {
  const {
    data: chatList,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useGetChatsInfiniteSuspenseQuery({
    params: {
      subject: [subject],
    },
  });
  const { observerRootRef, lastElementRef } = useInfiniteScroll({
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  });

  if (chatList.pages.every((page) => page.items.length === 0)) {
    return (
      <div className="flex flex-col gap-y-4 w-full items-center justify-center py-12">
        <div className="text-sm text-muted-foreground">채팅 기록이 없습니다.</div>
      </div>
    );
  }

  return (
    <div ref={observerRootRef} className="flex flex-col gap-y-4 pb-8">
      <ul className="flex flex-col gap-y-4" aria-label="채팅 목록">
        {chatList.pages.map((page) =>
          page.items.map((chat) => (
            <li key={chat.id}>
              <ChatListCard chat={chat} />
            </li>
          )),
        )}
      </ul>

      <div ref={lastElementRef} />

      {isFetchingNextPage && (
        <div className="flex items-center justify-center py-4">
          <div className="text-sm text-gray-500">로딩 중...</div>
        </div>
      )}
    </div>
  );
}

export function ChatHistoryListSkeleton() {
  return (
    <div className="flex flex-col gap-y-4 pb-8">
      {Array.from({ length: 10 }).map((_, index) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: 스켈레톤 컴포넌트 인덱스 키
        <Skeleton key={index} className="h-17.5 w-full" />
      ))}
    </div>
  );
}
