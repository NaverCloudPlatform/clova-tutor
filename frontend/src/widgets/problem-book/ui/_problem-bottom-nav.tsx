/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { Link, useParams, useSearch } from '@tanstack/react-router';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { useProblemIndex } from '@/entities/problems/hook/use-problem-index';
import { Button } from '@/shared/ui/button';
import { Skeleton } from '@/shared/ui/skeleton';
import { cn } from '@/shared/utils/utils';

export function ProblemBottomNav() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id/problem',
  });
  const { problem_id: problemId } = useSearch({
    from: '/_student/$subject/chats/$chat_id/problem',
  });
  const { data: problems } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblems({
      chatId: Number(chatId),
    }),
  });
  const { subject } = useSubject();
  const { currentProblemNumber, currentProblemIndex } = useProblemIndex({
    chatId,
    problemId,
  });
  const totalProblems = problems.length;

  return (
    <div className="flex items-center justify-between px-4 py-3 gap-x-4 border-t">
      <Link
        className={cn('flex items-center gap-x-1', currentProblemNumber <= 1 && 'pointer-events-none')}
        from={`/$subject/chats/$chat_id/problem`}
        to={`/$subject/chats/$chat_id/problem`}
        params={{
          subject,
          chat_id: chatId,
        }}
        search={{
          problem_id: problems[currentProblemIndex - 1]?.id,
        }}
      >
        <Button variant="ghost" size="sm" className="text-muted-foreground" disabled={currentProblemNumber <= 1}>
          <ChevronLeft className="w-4 h-4" />
          이전
        </Button>
      </Link>

      <div className="flex items-center gap-x-1 text-sm">
        <span className="font-medium">{currentProblemNumber}</span>
        <span className="text-muted-foreground">/ {totalProblems}</span>
      </div>

      <Link
        className={cn('flex items-center gap-x-1', currentProblemNumber >= totalProblems && 'pointer-events-none')}
        from={`/$subject/chats/$chat_id/problem`}
        to={`/$subject/chats/$chat_id/problem`}
        params={{
          subject,
          chat_id: chatId,
        }}
        search={{
          problem_id: problems[currentProblemIndex + 1]?.id,
        }}
      >
        <Button
          variant="ghost"
          size="sm"
          className="text-muted-foreground"
          disabled={currentProblemNumber >= totalProblems}
        >
          다음
          <ChevronRight className="w-4 h-4" />
        </Button>
      </Link>
    </div>
  );
}

export function ProblemBottomNavSkeleton() {
  return (
    <div className="flex items-center justify-between px-4 py-3 gap-x-4 border-t">
      <Skeleton className="w-10 h-10" />
      <Skeleton className="w-10 h-10" />
    </div>
  );
}
