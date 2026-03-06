/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import type { z } from 'zod';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { ProblemMetadataBadge, ProblemMetadataBadgeSkeleton } from '@/entities/problems/ui/problem-metadata-badge';
import type { searchSchema } from '../..';

type ProblemMetadataProps = Omit<
  NonNullable<
    NonNullable<z.infer<typeof searchSchema>['modal']>['type'] extends 'bookmarked-problem'
      ? z.infer<typeof searchSchema>['modal']
      : never
  >,
  'type'
>;

export function ProblemMetadata({ chatId, problemId }: ProblemMetadataProps) {
  const { data: problem } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      chatId: chatId,
      problemId: problemId,
    }),
    select: (data) => data.problem_info.content,
  });

  return (
    <ProblemMetadataBadge
      grade={problem.grade}
      level={problem.level}
      category={problem.category}
      classNames={{
        star: 'size-4.5',
        text: 'text-xl text-foreground font-semibold',
      }}
    />
  );
}

export function ProblemMetadataSkeleton() {
  return (
    <ProblemMetadataBadgeSkeleton
      classNames={{
        star: 'size-4.5',
        text: 'w-30 sm:w-80 h-7',
      }}
    />
  );
}
