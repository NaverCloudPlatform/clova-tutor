/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useNavigate, useSearch } from '@tanstack/react-router';
import { Suspense } from 'react';
import type { z } from 'zod';
import { GoalComplete } from '@/features/goal-system/ui/goal-complete';
import { ApiErrorBoundary } from '@/shared/ui/api-error-boundary';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/shared/ui/dialog';
import type { searchSchema } from '../..';
import { BookmarkedProblemContent, BookmarkedProblemContentSkeleton } from './_bookmarked-problem-content';
import { ProblemGoalsGuide } from './_problem-goals-guide';
import { ProblemMetadata, ProblemMetadataSkeleton } from './_problem-metadata';
import { ProblemNavigator, ProblemNavigatorSkeleton } from './problem-navigator';

export function BookmarkedProblemDialog() {
  const navigate = useNavigate();
  const { modal } = useSearch({ from: '/_student/$subject/problems/bookmark/' });

  const handleDialogClose = () => {
    navigate({
      to: '.',
      search: (prev) => ({
        ...prev,
        modal: undefined,
      }),
    });
  };

  if (modal?.type !== 'bookmarked-problem') return null;

  return (
    <Dialog open={modal?.type === 'bookmarked-problem'} onOpenChange={handleDialogClose}>
      <BookmarkedProblemDialogContent problemId={modal.problemId} chatId={modal.chatId} />
    </Dialog>
  );
}

type BookmarkedProblemDialogContentProps = Omit<
  NonNullable<
    NonNullable<z.infer<typeof searchSchema>['modal']>['type'] extends 'bookmarked-problem'
      ? z.infer<typeof searchSchema>['modal']
      : never
  >,
  'type'
>;

function BookmarkedProblemDialogContent({ problemId, chatId }: BookmarkedProblemDialogContentProps) {
  const handleInteractOutside = (e: Event) => {
    // MathLive 가상 키보드가 열려있으면 다이얼로그 닫힘 방지
    if (window.mathVirtualKeyboard?.visible) {
      e.preventDefault();
      return;
    }

    // composedPath로 Shadow DOM 내부 요소 확인
    const path = e.composedPath();
    const isVirtualKeyboard = path.some(
      (el) => el instanceof HTMLElement && el.tagName?.toLowerCase() === 'math-virtual-keyboard',
    );
    if (isVirtualKeyboard) {
      e.preventDefault();
    }
  };

  return (
    <DialogContent
      className="flex flex-col max-w-full sm:max-w-4xl min-h-2/3 h-full sm:h-auto rounded-none sm:rounded-lg"
      onPointerDownOutside={handleInteractOutside}
      onInteractOutside={handleInteractOutside}
    >
      <ApiErrorBoundary>
        <DialogHeader>
          <DialogTitle className="flex justify-between items-end py-4 px-0 sm:px-13 sm:h-17">
            <div className="flex md:flex-row flex-col gap-x-2">
              <div className="flex flex-col gap-y-2">
                <Suspense fallback={<ProblemMetadataSkeleton />}>
                  <ProblemMetadata chatId={chatId} problemId={problemId} />
                </Suspense>
              </div>

              <Suspense fallback={null}>
                <ProblemGoalsGuide chatId={chatId} problemId={problemId} />
              </Suspense>
            </div>

            <DialogDescription className="sr-only">학습컨텐츠 다이얼로그</DialogDescription>
          </DialogTitle>
        </DialogHeader>

        <Suspense
          fallback={
            <ProblemNavigatorSkeleton>
              <BookmarkedProblemContentSkeleton />
            </ProblemNavigatorSkeleton>
          }
        >
          <ProblemNavigator problemId={problemId} chatId={chatId}>
            <BookmarkedProblemContent problemId={problemId} chatId={chatId} />
          </ProblemNavigator>
        </Suspense>

        <GoalComplete chatId={chatId} />
      </ApiErrorBoundary>
    </DialogContent>
  );
}
