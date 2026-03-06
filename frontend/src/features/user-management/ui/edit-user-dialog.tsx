/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Pencil } from 'lucide-react';
import { useState } from 'react';
import { usePatchUsersByUserIdMutation } from '@/entities/users/__generated__/api/mutations';
import { UserForm, type UserFormData } from '@/entities/users/ui/user-form';
import type { UserResponseDto } from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui/dialog';

interface EditUserDialogProps {
  user: UserResponseDto;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children?: React.ReactNode;
}

export function EditUserDialog({ user, open: controlledOpen, onOpenChange, children }: EditUserDialogProps) {
  const { mutate: updateUser, isPending } = usePatchUsersByUserIdMutation();
  const [internalOpen, setInternalOpen] = useState(false);

  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;

  const setOpen = (newOpen: boolean) => {
    if (!isPending) {
      onOpenChange?.(newOpen);
      if (!isControlled) {
        setInternalOpen(newOpen);
      }
    }
  };

  const onSubmit = async (data: UserFormData) => {
    updateUser(
      {
        userId: user.id,
        payload: {
          name: data.name.trim(),
          grade: data.grade,
        },
      },
      {
        onSuccess: () => {
          setOpen(false);
        },
      },
    );
  };

  if (children) {
    return (
      <Dialog open={open} onOpenChange={setOpen}>
        {children}
        <EditUserDialogContent user={user} isPending={isPending} setOpen={setOpen} onSubmit={onSubmit} />
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {!isControlled && (
        <DialogTrigger asChild>
          <Button size="sm" variant="ghost" className="w-full justify-start">
            <Pencil className="w-4 h-4 mr-2" />
            수정
          </Button>
        </DialogTrigger>
      )}
      <EditUserDialogContent user={user} isPending={isPending} setOpen={setOpen} onSubmit={onSubmit} />
    </Dialog>
  );
}

type EditUserDialogContentProps = {
  user: UserResponseDto;
  isPending: boolean;
  setOpen: (open: boolean) => void;
  onSubmit: (data: UserFormData) => void;
};

function EditUserDialogContent({ user, isPending, setOpen, onSubmit }: EditUserDialogContentProps) {
  return (
    <DialogContent className="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>계정 정보 수정</DialogTitle>
        <DialogDescription>수정하고 싶은 내용을 입력해주세요.</DialogDescription>
      </DialogHeader>
      <UserForm
        defaultValues={{
          name: user.name,
          grade: user.grade,
        }}
        onSubmit={onSubmit}
        isSubmitting={isPending}
        hiddenFields={['grade']}
      >
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={isPending}>
            취소
          </Button>
          <Button type="submit" disabled={isPending}>
            {isPending ? '수정 중...' : '수정'}
          </Button>
        </DialogFooter>
      </UserForm>
    </DialogContent>
  );
}

EditUserDialog.Trigger = DialogTrigger;
