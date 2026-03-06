/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { Link, useParams, useSearch } from '@tanstack/react-router';
import { ChevronDownIcon } from 'lucide-react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { ProblemMetadataBadge } from '@/entities/problems/ui/problem-metadata-badge';
import { ProblemStatusBadge } from '@/entities/problems/ui/problem-status-badge';
import type { ChatProblemResponseDto } from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/shared/ui/dropdown-menu';
import { cn } from '@/shared/utils/utils';

export function ProblemNavigatorDropdown() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="secondary" className="w-fit h-6 rounded-2xl text-xs text-muted-foreground group">
          내가 푼 문제
          <ChevronDownIcon className="size-4 group-data-[state=open]:-rotate-180 transition-transform duration-100" />
        </Button>
      </DropdownMenuTrigger>
      <ProblemNavigatorItemSelectContent />
    </DropdownMenu>
  );
}

function ProblemNavigatorItemSelectContent() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id/problem',
  });
  const { data: problems } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblems({
      chatId: Number(chatId),
    }),
    select: (data) => data.sort((a, b) => a.number - b.number).map((problem) => problem.id),
  });

  return (
    <DropdownMenuContent align="start" className="w-80 me-3 md:me-5 md:max-h-90 flex flex-col gap-y-1 p-2">
      {problems.map((problemId) => (
        <ProblemNavigatorItem key={problemId} problemId={problemId} />
      ))}
    </DropdownMenuContent>
  );
}

type ProblemNavigatorItemProps = {
  problemId: ChatProblemResponseDto['id'];
};

function ProblemNavigatorItem({ problemId }: ProblemNavigatorItemProps) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id/problem',
  });
  const { problem_id: currentProblemId } = useSearch({
    from: '/_student/$subject/chats/$chat_id/problem',
  });
  const { data: problem } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblems({
      chatId: Number(chatId),
    }),
    select: (data) => data.find((problem) => problem.id === problemId),
  });
  const { subject } = useSubject();
  const isCurrentProblem = currentProblemId === problem?.id;

  if (!problem) return null;

  return (
    <Link
      to={`/$subject/chats/$chat_id/problem`}
      from={`/$subject/chats/$chat_id/problem`}
      params={{ subject, chat_id: chatId }}
      search={{
        problem_id: problem.id,
      }}
      preload={false}
    >
      <DropdownMenuItem className={cn('flex items-start gap-x-2', isCurrentProblem && 'bg-secondary')}>
        <div className={cn('text-sm font-medium ps-2 py-2')}>{problem.number}</div>
        <div className={cn('px-3 py-2 rounded-xl flex flex-col gap-y-1')}>
          <div className="flex items-center gap-x-2">
            <ProblemStatusBadge className="size-5" status={problem.status} />
            <p className="text-sm font-semibold">{problem.status}</p>
          </div>
          <ProblemMetadataBadge grade={problem.grade} level={problem.level} category={problem.category ?? ''} />
        </div>
      </DropdownMenuItem>
    </Link>
  );
}

export function ProblemNavigatorDropdownSkeleton() {
  return (
    <div className="w-full">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="secondary" className="w-fit h-6 rounded-2xl text-xs text-muted-foreground group">
            내가 푼 문제
            <ChevronDownIcon className="size-4 group-data-[state=open]:-rotate-180 transition-transform duration-100" />
          </Button>
        </DropdownMenuTrigger>
      </DropdownMenu>
    </div>
  );
}
