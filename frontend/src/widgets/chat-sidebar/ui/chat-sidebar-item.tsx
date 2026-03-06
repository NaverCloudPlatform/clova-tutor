/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { MoreHorizontal } from 'lucide-react';
import { useState } from 'react';
import { ChatTitle } from '@/entities/chats/ui/chat-title';
import { ChatManagementDropdownMenu } from '@/features/chat-management/ui/chat-management-dropdown-menu';
import { ChatTitleEdit } from '@/features/chat-management/ui/chat-title-edit';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';
import { SidebarMenuAction, SidebarMenuSubButton, SidebarMenuSubItem } from '@/shared/ui/sidebar';
import { cn } from '@/shared/utils/utils';

type ChatSidebarItemProps = {
  chat: ChatResponseDto;
};

export function ChatSidebarItem({ chat }: ChatSidebarItemProps) {
  const { chat_id: chatId } = useParams({
    strict: false,
  });
  const [isEditing, setIsEditing] = useState(false);

  const toggleEdit = () => {
    setIsEditing((prev) => !prev);
  };

  return (
    <SidebarMenuSubItem className="relative group/item">
      <SidebarMenuSubButton asChild isActive={chat.id === Number(chatId)} className="px-0">
        {isEditing ? (
          <ChatTitleEdit
            chatId={chat.id}
            initialTitle={chat.title}
            onBlur={toggleEdit}
            classNames={{
              input: 'p-0 px-2 bg-sidebar-accent focus-visible:ring-1 focus-visible:ring-inset focus-visible:ring-ring',
            }}
          />
        ) : (
          <ChatTitle
            chat={chat}
            classNames={{
              title: cn(
                'max-w-56 md:[@media(hover:none)]:max-w-44 md:max-w-none md:group-hover/item:max-w-44 md:group-has-[[data-state=open]]/item:max-w-44 px-2',
              ),
            }}
          />
        )}
      </SidebarMenuSubButton>

      <ChatManagementDropdownMenu
        isEditing={isEditing}
        toggleEdit={toggleEdit}
        chat={chat}
        trigger={
          <SidebarMenuAction
            className={cn(
              'data-[state=open]:opacity-100 opacity-100 md:opacity-0 md:group-hover/item:opacity-100 transition-opacity',
              isEditing && 'hidden',
            )}
            aria-label="채팅방 옵션 열기"
          >
            <MoreHorizontal />
          </SidebarMenuAction>
        }
      />
    </SidebarMenuSubItem>
  );
}
