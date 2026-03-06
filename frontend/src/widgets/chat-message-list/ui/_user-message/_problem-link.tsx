/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { Link, useParams } from '@tanstack/react-router';
import { Suspense } from 'react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import {
  ProblemLinkBadgeLabelSkeleton,
  UserMessageProblemLinkBadgeLabel,
} from '@/entities/chats/ui/user-message/user-message-problem-link-badge-label';
import type { ChatProblemResponseDto, ProblemLinkContentDto } from '@/shared/api/__generated__/dto';

type ProblemLinkBadgeProps = {
  content: ProblemLinkContentDto;
};

export function ProblemLinkBadge(props: ProblemLinkBadgeProps) {
  const { content } = props;

  return (
    <Suspense fallback={<ProblemLinkBadgeLabelSkeleton />}>
      <ProblemLinkLabelLink problemId={content.value.problem_id} />
    </Suspense>
  );
}

function ProblemLinkLabelLink({ problemId }: { problemId: ChatProblemResponseDto['id'] }) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: problem } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      chatId: Number(chatId),
      problemId,
    }),
  });
  const { subject } = useSubject();

  return (
    <Link
      to={`/$subject/chats/$chat_id/problem`}
      params={{ subject, chat_id: chatId }}
      search={{
        problem_id: problemId,
      }}
    >
      <UserMessageProblemLinkBadgeLabel className="hover:underline" problemNumber={problem?.number} />
    </Link>
  );
}
