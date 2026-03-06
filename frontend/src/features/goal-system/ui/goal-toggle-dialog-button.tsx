/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { useParams } from '@tanstack/react-router';
import { GoalIcon } from 'lucide-react';
import { Suspense } from 'react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { Button } from '@/shared/ui/button';
import { Dialog, DialogTrigger } from '@/shared/ui/dialog';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/shared/ui/tooltip';
import { cn } from '@/shared/utils/utils';
import { GoalCreateDialogContent } from './goal-create-dialog-content';
import { GoalDeleteDialogContent } from './goal-delete-dialog-content';

export function GoalToggleDialogButton() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: hasActiveGoal } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatId({
      chatId: Number(chatId),
    }),
    select: (data) => {
      return data.has_active_goal;
    },
  });

  return (
    <Dialog>
      <Suspense fallback={<GoalToggleDialogSkeleton />}>
        <Tooltip>
          <TooltipTrigger asChild>
            <DialogTrigger asChild>
              <Button
                aria-label="학습 목표 설정"
                type="button"
                variant="outline"
                size="icon"
                className={cn(hasActiveGoal && 'border-chart-4 bg-chart-5')}
              >
                <GoalIcon className={cn('size-5', hasActiveGoal && 'stroke-primary')} />
              </Button>
            </DialogTrigger>
          </TooltipTrigger>
          <TooltipContent>
            <p>{hasActiveGoal ? '학습 목표를 취소해요' : '학습 목표를 설정해요'}</p>
          </TooltipContent>
        </Tooltip>
      </Suspense>

      {hasActiveGoal ? <GoalDeleteDialogContent /> : <GoalCreateDialogContent key={chatId} />}
    </Dialog>
  );
}

export function GoalToggleDialogSkeleton() {
  return (
    <Button type="button" variant="outline" size="icon" disabled>
      <GoalIcon className="size-5" />
    </Button>
  );
}
