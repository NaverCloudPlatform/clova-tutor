/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient } from '@tanstack/react-query';
import { PartyPopperIcon } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useChatProblemSubmitMutationState } from '@/entities/chats/hooks/use-chat-problem-submit-mutation-state';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';
import { eventManager } from '@/shared/core/event-manager';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/shared/ui/dialog';

type GoalCompleteProps = {
  chatId: ChatResponseDto['id'];
};

export function GoalComplete({ chatId }: GoalCompleteProps) {
  const queryClient = useQueryClient();
  const mutationStates = useChatProblemSubmitMutationState({
    chatId,
    status: 'success',
    select: (data) => {
      if (!data.active_goal) return false;

      return data.active_goal?.solved_count === data.active_goal?.goal_count;
    },
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const timer = useRef<NodeJS.Timeout | null>(null);
  const isCompleteGoal = mutationStates.at(-1);

  useEffect(() => {
    if (isCompleteGoal) {
      eventManager.emit('confetti-container');
      setDialogOpen(true);

      timer.current = setTimeout(() => {
        setDialogOpen(false);

        const mutationCache = queryClient.getMutationCache();
        const mutations = mutationCache.getAll();
        mutations.forEach((mutation) => {
          mutationCache.remove(mutation);
        });
      }, 2000);
    }
  }, [isCompleteGoal, queryClient]);

  useEffect(() => {
    return () => {
      if (timer.current) {
        clearTimeout(timer.current);
      }
    };
  }, []);

  return (
    <Dialog open={dialogOpen}>
      <DialogContent className="sm:max-w-md pt-12" classNames={{ overlay: 'bg-black/30' }} hideCloseButton>
        <DialogHeader className="space-y-3">
          <DialogTitle className="text-center">학습 목표 달성!</DialogTitle>
          <DialogDescription className="text-center">
            오늘도 스스로 세운 목표를 끝까지 해냈네! 정말 멋져👍
            <br />
            다음 목표도 함께 도전해보자!
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="flex flex-row justify-between sm:justify-between w-full">
          <PartyPopperIcon className="size-8 stroke-primary" />
          <PartyPopperIcon className="size-8 stroke-primary -rotate-z-100" />
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
