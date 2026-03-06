/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { UserPlus } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import { usePostUsersMutation } from '@/entities/users/__generated__/api/mutations';
import { UserForm, type UserFormData } from '@/entities/users/ui/user-form';
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

interface AddUserDialogProps {
  children?: React.ReactNode;
}

export function AddUserDialog({ children }: AddUserDialogProps) {
  const { mutate: addUser, isPending } = usePostUsersMutation();
  const [open, setOpen] = useState(false);

  const onSubmit = async (data: UserFormData) => {
    addUser(
      {
        payload: {
          name: data.name.trim(),
          grade: data.grade,
        },
      },
      {
        onSuccess: () => {
          setOpen(false);
        },
        onError: () => {
          toast.error('학생 추가에 실패했습니다. 다시 시도해주세요.');
        },
      },
    );
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!isPending) {
      setOpen(newOpen);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {children || (
          <Button size="sm">
            <UserPlus className="w-4 h-4 mr-2" />
            계정 만들기
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>새 학생 추가</DialogTitle>
          <DialogDescription>새로운 학생을 추가합니다. 이름과 학년을 입력해주세요.</DialogDescription>
        </DialogHeader>
        <UserForm onSubmit={onSubmit} isSubmitting={isPending}>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={isPending}>
              취소
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? '추가 중...' : '추가'}
            </Button>
          </DialogFooter>
        </UserForm>
      </DialogContent>
    </Dialog>
  );
}
