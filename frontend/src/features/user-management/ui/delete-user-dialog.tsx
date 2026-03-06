/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Trash2Icon } from 'lucide-react';
import { useState } from 'react';
import { useDeleteUsersByUserIdMutation } from '@/entities/users/__generated__/api/mutations';
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

type Props = {
  userId: string;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children?: React.ReactNode;
};

export function DeleteUserDialog({ userId, open: controlledOpen, onOpenChange, children }: Props) {
  const { mutate: deleteUser, isPending } = useDeleteUsersByUserIdMutation();
  const [internalOpen, setInternalOpen] = useState(false);

  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;

  const setOpen = (newOpen: boolean) => {
    onOpenChange?.(newOpen);
    if (!isControlled) {
      setInternalOpen(newOpen);
    }
  };

  const handleDeleteUser = () => {
    deleteUser(
      { userId },
      {
        onSuccess: () => {
          setOpen(false);
        },
      },
    );
  };

  if (children) {
    return (
      <AlertDialog open={open} onOpenChange={setOpen}>
        {children}
        <DeleteUserDialogContent isPending={isPending} handleDeleteUser={handleDeleteUser} />
      </AlertDialog>
    );
  }

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      {!isControlled && (
        <AlertDialogTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start rounded-sm hover:bg-destructive/10 text-destructive"
          >
            <Trash2Icon className="size-4 me-2 stroke-destructive" />
            삭제
          </Button>
        </AlertDialogTrigger>
      )}
      <DeleteUserDialogContent isPending={isPending} handleDeleteUser={handleDeleteUser} />
    </AlertDialog>
  );
}

type DeleteUserDialogContentProps = {
  isPending: boolean;
  handleDeleteUser: () => void;
};

function DeleteUserDialogContent({ isPending, handleDeleteUser }: DeleteUserDialogContentProps) {
  return (
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>정말 계정을 삭제하시겠습니까?</AlertDialogTitle>
        <AlertDialogDescription>이 작업은 되돌릴 수 없습니다. 계정이 영구적으로 삭제됩니다.</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>취소</AlertDialogCancel>
        <AlertDialogAction onClick={handleDeleteUser} disabled={isPending}>
          {isPending ? '삭제 중...' : '삭제'}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  );
}

DeleteUserDialog.Trigger = AlertDialogTrigger;
