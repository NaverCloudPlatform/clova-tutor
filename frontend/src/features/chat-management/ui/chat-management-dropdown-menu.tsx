/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { MoreHorizontal, PenLineIcon, Trash2 } from 'lucide-react';
import { ChatDeleteDialog } from '@/features/chat-management/ui/chat-delete-dialog';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/shared/ui/dropdown-menu';
import { cn } from '@/shared/utils/utils';

type ChatDropdownMenuProps = {
  isEditing: boolean;
  toggleEdit: () => void;
  chat: ChatResponseDto;
  trigger?: React.ReactNode;
};

export function ChatManagementDropdownMenu({ isEditing, toggleEdit, chat, trigger }: ChatDropdownMenuProps) {
  return (
    <ChatDeleteDialog chatId={chat.id} title={chat.title}>
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          {trigger ?? (
            <Button variant="ghost" size="icon" className={cn(isEditing && 'invisible')} aria-label="채팅방 옵션 열기">
              <MoreHorizontal />
            </Button>
          )}
        </DropdownMenuTrigger>
        <DropdownMenuContent side="right" align="start" className={cn(isEditing && 'hidden')}>
          <DropdownMenuItem onClick={toggleEdit}>
            <PenLineIcon />
            이름 바꾸기
          </DropdownMenuItem>

          <ChatDeleteDialog.Trigger asChild>
            <DropdownMenuItem variant="destructive">
              <Trash2 className="h-4 w-4 stroke-destructive" />
              <span className="text-destructive">삭제</span>
            </DropdownMenuItem>
          </ChatDeleteDialog.Trigger>
        </DropdownMenuContent>
      </DropdownMenu>
    </ChatDeleteDialog>
  );
}
