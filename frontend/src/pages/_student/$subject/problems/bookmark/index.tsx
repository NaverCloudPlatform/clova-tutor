/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { ClipboardPenLineIcon } from 'lucide-react';
import { z } from 'zod';
import { ApiErrorBoundary } from '@/packages/error-boundary';
import { problemStatusDtoSchema } from '@/shared/api/__generated__/schema';
import { useIsMobile } from '@/shared/hooks/use-mobile';
import { BookmarkedProblemDialog } from './-components/dialog/bookmarked-problem-dialog';
import { ProblemBookmarkListTab } from './-components/tabs/problem-bookmark-list-tab';

export const searchSchema = z.object({
  status: problemStatusDtoSchema.array().optional(),
  modal: z
    .discriminatedUnion('type', [
      z.object({
        type: z.literal('bookmarked-problem'),
        problemId: z.string(),
        chatId: z.number(),
      }),
    ])
    .optional(),
});

export const Route = createFileRoute('/_student/$subject/problems/bookmark/')({
  component: RouteComponent,
  validateSearch: zodValidator(searchSchema),
  head: ({ params: { subject } }) => {
    const title = `${subject === 'math' ? '수학' : '영어'} 학습 노트`;

    return {
      meta: [
        {
          title,
        },
      ],
    };
  },
});

function RouteComponent() {
  const isMobile = useIsMobile();

  return (
    <div className="w-full space-y-8">
      <header className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          {!isMobile && <ClipboardPenLineIcon className="size-6 stroke-primary" />}
          <h1 className="text-xl sm:text-2xl font-bold">학습 노트</h1>
        </div>
        <p className="text-foreground-weak text-sm sm:text-base">
          원하는 문제를 저장하고, 오답 문제는 다시 풀어볼 수 있어요
        </p>
      </header>

      <ApiErrorBoundary>
        <ProblemBookmarkListTab />
        <BookmarkedProblemDialog />
      </ApiErrorBoundary>
    </div>
  );
}
