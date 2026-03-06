/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import type { z } from 'zod';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { GoalProgressStatus } from '@/entities/goals/ui/goal-progress-status';
import type { searchSchema } from '../..';

type ProblemGoalsGuideProps = Pick<
  NonNullable<
    NonNullable<z.infer<typeof searchSchema>['modal']>['type'] extends 'bookmarked-problem'
      ? z.infer<typeof searchSchema>['modal']
      : never
  >,
  'chatId' | 'problemId'
>;

export function ProblemGoalsGuide({ chatId, problemId }: ProblemGoalsGuideProps) {
  const { data: activeGoal } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatId({
      chatId: Number(chatId),
    }),
    select: (data) => {
      return data.active_goal;
    },
  });

  const { data: isProblemSolved } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      chatId: Number(chatId),
      problemId: problemId,
    }),
    select: (data) => {
      return data.status === '정답' || data.status === '복습 완료';
    },
  });

  if (!activeGoal || isProblemSolved) return null;

  return (
    <div className="flex items-end gap-x-2">
      <p className="text-sm font-normal text-primary pb-1">
        이 문제를 맞추면 <b>학습 목표</b>를 달성할 수 있어!
      </p>
      <GoalProgressStatus chatId={chatId} />
    </div>
  );
}
