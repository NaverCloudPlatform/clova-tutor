/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { useParams } from '@tanstack/react-router';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';

export function ActiveGoalsPlaceholder() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: remainingGoalCount } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatId({
      chatId: Number(chatId),
    }),
    select: (data) => {
      if (!data.has_active_goal || !data.active_goal) return null;

      const { goal_count, solved_count } = data.active_goal;
      return goal_count - solved_count;
    },
  });

  return remainingGoalCount
    ? `이제 목표 달성까지 ${remainingGoalCount}문제 남았네! 같이 힘내보자~`
    : '궁금한 것이 있다면 언제든 물어봐!';
}

export function ActiveGoalsPlaceholderSkeleton() {
  return '궁금한 것이 있다면 언제든 물어봐!';
}
