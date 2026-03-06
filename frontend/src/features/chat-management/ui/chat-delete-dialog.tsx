/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams, useRouter } from '@tanstack/react-router';
import { Trash2 } from 'lucide-react';
import type { PropsWithChildren } from 'react';
import { useState } from 'react';
import { useDeleteChatsByChatIdMutation } from '@/entities/chats/__generated__/api/mutations';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { useChatStore } from '@/entities/chats/store/chats';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/shared/ui/alert-dialog';
import { Button } from '@/shared/ui/button';
import { useSidebar } from '@/shared/ui/sidebar';

type ChatDeleteDialogProps = {
  chatId: number;
  title: string;
} & PropsWithChildren;

export function ChatDeleteDialog({ chatId, title, children }: ChatDeleteDialogProps) {
  const router = useRouter();
  const { chat_id: currentPageChatId } = useParams({
    strict: false,
  });
  const removeChatInput = useChatStore((state) => state.removeChatInput);
  const { subject } = useSubject();
  const { setOpenMobile } = useSidebar();
  const [open, setOpen] = useState(false);

  const { mutate: deleteChat, isPending } = useDeleteChatsByChatIdMutation({
    onSuccess: () => {
      removeChatInput(chatId);
      setOpen(false);
      setOpenMobile(false);

      if (Number(currentPageChatId) === chatId) {
        router.navigate({
          to: '/$subject/chats',
          params: {
            subject,
          },
          replace: true,
        });
      }
    },
  });

  const handleDeleteChat = () => {
    deleteChat({ chatId });
  };

  if (children) {
    return (
      <AlertDialog open={open} onOpenChange={setOpen}>
        {children}
        <ChatDeleteDialogContent title={title} isPending={isPending} onDelete={handleDeleteChat} />
      </AlertDialog>
    );
  }

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button variant="ghost" size="sm" className="w-full justify-start rounded-sm hover:bg-destructive/10">
          <Trash2 className="h-4 w-4 stroke-destructive" />
          <span className="text-destructive">삭제</span>
        </Button>
      </AlertDialogTrigger>
      <ChatDeleteDialogContent title={title} isPending={isPending} onDelete={handleDeleteChat} />
    </AlertDialog>
  );
}

type ChatDeleteDialogContentProps = {
  title: string;
  isPending: boolean;
  onDelete: () => void;
};

function ChatDeleteDialogContent({ title, isPending, onDelete }: ChatDeleteDialogContentProps) {
  return (
    <AlertDialogContent
      onOpenAutoFocus={(e) => {
        e.preventDefault();
        const firstButton = (e.currentTarget as HTMLElement).querySelector('button');
        firstButton?.focus();
      }}
    >
      <AlertDialogHeader>
        <AlertDialogTitle className="wrap-anywhere">"{title}" 대화를 삭제하시겠습니까?</AlertDialogTitle>
        <AlertDialogDescription>삭제된 대화는 복구할 수 없습니다.</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel disabled={isPending}>취소</AlertDialogCancel>
        <AlertDialogAction onClick={onDelete} disabled={isPending}>
          {isPending ? '삭제 중...' : '삭제'}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  );
}

ChatDeleteDialog.Trigger = AlertDialogTrigger;
