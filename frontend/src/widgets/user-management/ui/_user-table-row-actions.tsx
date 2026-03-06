/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { MoreVerticalIcon, Pencil, Trash2Icon } from 'lucide-react';
import { DeleteUserDialog } from '@/features/user-management/ui/delete-user-dialog';
import { EditUserDialog } from '@/features/user-management/ui/edit-user-dialog';
import type { UserResponseDto } from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/shared/ui/dropdown-menu';

type UserTableRowActionsProps = {
  user: UserResponseDto;
};

export function UserTableRowActions({ user }: UserTableRowActionsProps) {
  return (
    <EditUserDialog user={user}>
      <DeleteUserDialog userId={user.id}>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVerticalIcon className="h-4 w-4" />
              <span className="sr-only">메뉴 열기</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="min-w-25 w-25">
            <EditUserDialog.Trigger asChild>
              <DropdownMenuItem>
                <Pencil className="size-4" />
                수정
              </DropdownMenuItem>
            </EditUserDialog.Trigger>
            <DeleteUserDialog.Trigger asChild>
              <DropdownMenuItem variant="destructive">
                <Trash2Icon className="size-4" />
                삭제
              </DropdownMenuItem>
            </DeleteUserDialog.Trigger>
          </DropdownMenuContent>
        </DropdownMenu>
      </DeleteUserDialog>
    </EditUserDialog>
  );
}
