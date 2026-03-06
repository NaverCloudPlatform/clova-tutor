/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { EllipsisIcon } from 'lucide-react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import type { SubjectEnumDto } from '@/shared/api/__generated__/dto';
import { SidebarMenuSubButton, SidebarMenuSubItem } from '@/shared/ui/sidebar';
import { Skeleton } from '@/shared/ui/skeleton';
import { CHAT_LIST_SIZE } from '../constants/chat-list';
import { ChatSidebarItem } from './chat-sidebar-item';

type ChatListProps = {
  subject: SubjectEnumDto;
};

export function ChatList({ subject }: ChatListProps) {
  const { data: chatList } = useSuspenseQuery({
    ...chatsQueries.getChats({
      params: {
        subject: [subject],
        size: CHAT_LIST_SIZE,
      },
    }),
  });

  return (
    <>
      {chatList.items.map((chat) => (
        <ChatSidebarItem key={chat.id} chat={chat} />
      ))}

      <SidebarMenuSubItem>
        <SidebarMenuSubButton className="text-foreground-weak" asChild>
          <Link to="/$subject/chats/history" params={{ subject }}>
            <EllipsisIcon className="border rounded" />
            모든 채팅
          </Link>
        </SidebarMenuSubButton>
      </SidebarMenuSubItem>
    </>
  );
}

export function ChatListSkeleton() {
  return (
    <div className="flex flex-col gap-2">
      {Array.from({ length: 10 }).map((_, index) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: 스켈레톤 컴포넌트 인덱스 키
        <Skeleton key={index} className="h-8 w-full rounded-md" />
      ))}
    </div>
  );
}
