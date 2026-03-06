/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import type { ProblemResponseDto } from '@/shared/api/__generated__/dto';

type Props = {
  chatId: string;
  problemId: ProblemResponseDto['id'];
};

export function useProblemIndex({ chatId, problemId }: Props) {
  const { data: problems } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblems({
      chatId: Number(chatId),
    }),
  });

  const currentProblemIndex = problems.findIndex((problem) => problem.id === problemId);

  return {
    currentProblemNumber: currentProblemIndex + 1,
    currentProblemIndex,
  };
}
