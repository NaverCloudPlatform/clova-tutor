/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient } from '@tanstack/react-query';
import { useMatch, useParams, useRouter } from '@tanstack/react-router';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { useProblemStore } from '@/entities/problems/store/problem';
import type { ChatProblemResponseDto } from '@/shared/api/__generated__/dto';

export function useStudyArea() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const isStudyAreaOpen = !!useMatch({
    from: '/_student/$subject/chats/$chat_id/problem',
    shouldThrow: false,
  });
  const { subject } = useSubject();

  const goToProblem = async (problemId: ChatProblemResponseDto['id']) => {
    await router.navigate({
      to: '/$subject/chats/$chat_id/problem',
      params: {
        subject,
        chat_id: chatId,
      },
      search: {
        problem_id: problemId,
      },
    });
  };

  const closeStudyArea = async () => {
    await router.navigate({
      to: '/$subject/chats/$chat_id',
      params: {
        subject,
        chat_id: chatId,
      },
    });
  };

  const openStudyArea = async () => {
    const lastProblemId = useProblemStore.getState().getLastProblemId(Number(chatId));

    if (lastProblemId) {
      await goToProblem(lastProblemId);
      return;
    }

    const data = await queryClient.ensureQueryData({
      ...chatsQueries.getChatsByChatIdProblems({
        chatId: Number(chatId),
      }),
    });

    await goToProblem(data[0].id);
  };

  const toggleStudyArea = () => {
    const toggleFunction = isStudyAreaOpen ? closeStudyArea : openStudyArea;

    toggleFunction();
  };

  return {
    isStudyAreaOpen,
    toggleStudyArea,
    goToProblem,
    openStudyArea,
    closeStudyArea,
  };
}
