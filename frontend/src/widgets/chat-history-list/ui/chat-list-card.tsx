/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { format } from 'date-fns';
import { useState } from 'react';
import { ChatFooterBadges } from '@/entities/chats/ui/chat-footer-badges';
import { ChatHeaderBadges } from '@/entities/chats/ui/chat-header-badges';
import { ChatTitle } from '@/entities/chats/ui/chat-title';
import { ChatManagementDropdownMenu } from '@/features/chat-management/ui/chat-management-dropdown-menu';
import { ChatTitleEdit } from '@/features/chat-management/ui/chat-title-edit';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';

type ChatListCardProps = {
  chat: ChatResponseDto;
};

export function ChatListCard({ chat }: ChatListCardProps) {
  const [isEditing, setIsEditing] = useState(false);

  const toggleEdit = () => {
    setIsEditing((prev) => !prev);
  };

  return (
    <div className="flex justify-between items-center border rounded-md p-4 bg-card">
      <div className="flex flex-col gap-1 w-full">
        <ChatHeaderBadges chat={chat} />
        <div className="flex flex-col flex-1 w-full">
          {isEditing ? (
            <ChatTitleEdit
              chatId={chat.id}
              initialTitle={chat.title}
              onBlur={toggleEdit}
              className="w-full"
              classNames={{ input: 'h-6 p-0 font-semibold !text-base rounded-none w-full bg-sidebar-accent rounded' }}
            />
          ) : (
            <ChatTitle chat={chat} classNames={{ title: 'font-semibold text-base' }} />
          )}
        </div>
        <p className="text-xs text-foreground-weak mb-1">
          마지막 학습: {format(new Date(chat.latest_used_at), 'yyyy-MM-dd HH:mm')}
        </p>
        <ChatFooterBadges chat={chat} />
      </div>

      <ChatManagementDropdownMenu isEditing={isEditing} toggleEdit={toggleEdit} chat={chat} />
    </div>
  );
}
