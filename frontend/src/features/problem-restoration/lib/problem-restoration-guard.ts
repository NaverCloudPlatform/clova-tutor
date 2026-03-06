/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { RegisteredRouter, ValidateRedirectOptions } from '@tanstack/react-router';
import { queryClient } from '@/app/provider/tanstack-query';
import type { FileRoutesByFullPath } from '@/app/routes/routeTree.gen';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useProblemStore } from '@/entities/problems/store/problem';

type ProblemRestorationGuard = Parameters<
  NonNullable<FileRoutesByFullPath['/$subject/chats/$chat_id']['options']['beforeLoad']>
>[0];

const MOBILE_BREAKPOINT = 768;

export async function problemRestorationGuard({ params, matches }: ProblemRestorationGuard) {
  const isMobile = typeof window !== 'undefined' && window.innerWidth < MOBILE_BREAKPOINT;
  if (isMobile) {
    return;
  }

  const { chat_id } = params;
  const { getLastProblemId, resetLastProblemId } = useProblemStore.getState();
  const lastProblemId = getLastProblemId(Number(chat_id));
  const isChatPage = matches.at(-1)?.routeId === '/_student/$subject/chats/$chat_id';

  if (!isChatPage || !lastProblemId) {
    return;
  }

  try {
    const problems = await queryClient.ensureQueryData(
      chatsQueries.getChatsByChatIdProblems({ chatId: Number(chat_id) }),
    );
    const isProblemExists = problems.find((problem) => problem.id === lastProblemId);

    if (!isProblemExists) {
      resetLastProblemId(Number(chat_id));
      return;
    }

    const redirectOptions = {
      from: '/$subject/chats/$chat_id',
      to: '/$subject/chats/$chat_id/problem',
      params,
      search: {
        problem_id: lastProblemId,
      },
    } as const;

    return redirectOptions as ValidateRedirectOptions<RegisteredRouter, typeof redirectOptions>;
  } catch {
    resetLastProblemId(Number(chat_id));
    return;
  }
}
