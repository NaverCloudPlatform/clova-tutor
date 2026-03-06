/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { useParams } from '@tanstack/react-router';
import { SparklesIcon } from 'lucide-react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useDeleteGoalsByGoalIdMutation } from '@/entities/goals/__generated__/api/mutations';
import { Button } from '@/shared/ui/button';
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog';

export function GoalDeleteDialogContent() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: goalId } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatId({
      chatId: Number(chatId),
    }),
    select: (data) => {
      return data.active_goal?.id;
    },
  });
  const { mutate: deleteGoal } = useDeleteGoalsByGoalIdMutation();

  if (!goalId) return null;

  const handleDeleteGoal = () => {
    deleteGoal({
      goalId: goalId,
    });
  };

  return (
    <DialogContent onCloseAutoFocus={(e) => e.preventDefault()}>
      <DialogHeader>
        <DialogTitle>학습 목표 취소</DialogTitle>
        <DialogDescription className="flex gap-x-2">
          <SparklesIcon className="size-4 stroke-primary mt-0.5" />
          목표를 끝까지 함께 달성하면 뿌듯할 거예요!
          <br />
          그래도 정말 취소하시겠어요?
        </DialogDescription>
      </DialogHeader>

      <DialogFooter>
        <DialogClose asChild>
          <Button type="button" variant="default">
            아니오
          </Button>
        </DialogClose>

        <DialogClose asChild>
          <Button type="submit" variant="secondary" onClick={handleDeleteGoal}>
            네
          </Button>
        </DialogClose>
      </DialogFooter>
    </DialogContent>
  );
}
