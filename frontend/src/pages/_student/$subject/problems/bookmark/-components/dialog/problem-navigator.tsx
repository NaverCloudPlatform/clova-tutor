/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useNavigate, useSearch } from '@tanstack/react-router';
import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';
import type { PropsWithChildren } from 'react';
import { useMemo } from 'react';
import type { z } from 'zod';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { useGetProblemBookmarksInfiniteSuspenseQuery } from '@/entities/problem-bookmarks/api/queries/use-get-problem-bookmarks-infinite-query';
import { useIsMobile } from '@/shared/hooks/use-mobile';
import { Button } from '@/shared/ui/button';
import type { searchSchema } from '../..';
import { PROBLEM_BOOKMARK_LIST_PAGE_SIZE } from '../../-constants/common';

type ProblemNavigatorProps = PropsWithChildren &
  Omit<
    NonNullable<
      NonNullable<z.infer<typeof searchSchema>['modal']>['type'] extends 'bookmarked-problem'
        ? z.infer<typeof searchSchema>['modal']
        : never
    >,
    'type'
  >;

export function ProblemNavigator({ children, problemId, chatId }: ProblemNavigatorProps) {
  const navigate = useNavigate();
  const { status } = useSearch({ from: '/_student/$subject/problems/bookmark/' });
  const { subject } = useSubject();
  const {
    data: bookmarkedProblems,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useGetProblemBookmarksInfiniteSuspenseQuery({
    params: {
      subject,
      status,
      size: PROBLEM_BOOKMARK_LIST_PAGE_SIZE,
    },
  });
  const isMobile = useIsMobile();

  const currentPosition = useMemo(() => {
    for (let pageIndex = 0; pageIndex < bookmarkedProblems.pages.length; pageIndex++) {
      const page = bookmarkedProblems.pages[pageIndex];
      const itemIndex = page.items.findIndex(
        (item) => item.chat.id === chatId && item.problem.problem_info.id === problemId,
      );
      if (itemIndex !== -1) return { pageIndex, itemIndex };
    }
    return null;
  }, [bookmarkedProblems.pages, chatId, problemId]);

  const previousItem = useMemo(() => {
    if (!currentPosition) return null;
    const { pageIndex, itemIndex } = currentPosition;

    if (itemIndex > 0) return bookmarkedProblems.pages[pageIndex].items[itemIndex - 1];
    if (pageIndex > 0) {
      const prevPage = bookmarkedProblems.pages[pageIndex - 1];
      return prevPage.items[prevPage.items.length - 1];
    }
    return null;
  }, [currentPosition, bookmarkedProblems.pages]);

  const nextItem = useMemo(() => {
    if (!currentPosition) return null;
    const { pageIndex, itemIndex } = currentPosition;
    const currentPage = bookmarkedProblems.pages[pageIndex];

    if (itemIndex < currentPage.items.length - 1) return currentPage.items[itemIndex + 1];
    if (pageIndex < bookmarkedProblems.pages.length - 1) return bookmarkedProblems.pages[pageIndex + 1].items[0];
    return null;
  }, [currentPosition, bookmarkedProblems.pages]);

  const hasPrevious = previousItem !== null;
  const hasNext = nextItem !== null || hasNextPage;

  const navigateToItem = (item: { chat: { id: number }; problem: { problem_info: { id: string } } }) => {
    navigate({
      to: '.',
      search: (prev) => ({
        ...prev,
        modal: {
          type: 'bookmarked-problem',
          chatId: item.chat.id,
          problemId: item.problem.problem_info.id,
        },
      }),
    });
  };

  const handlePrevious = () => {
    if (previousItem) navigateToItem(previousItem);
  };

  const handleNext = async () => {
    if (!currentPosition) return;

    if (nextItem) {
      navigateToItem(nextItem);
      return;
    }

    if (!hasNextPage || isFetchingNextPage) return;

    // 다음 페이지 로드 후 첫 번째 아이템으로 이동
    const result = await fetchNextPage();
    const newPage = result.data?.pages.at(-1);
    const firstItem = newPage?.items[0];
    if (firstItem) navigateToItem(firstItem);
  };

  if (isMobile) {
    return (
      <div className="flex flex-col gap-y-2 flex-1">
        <div className="flex-1">{children}</div>
        <div className="flex items-center justify-between gap-x-2">
          <Button variant="ghost" aria-label="이전 문제" onClick={handlePrevious} disabled={!hasPrevious}>
            <ChevronLeftIcon className="size-4" />
            이전 문제
          </Button>
          <Button variant="ghost" aria-label="다음 문제" onClick={handleNext} disabled={!hasNext || isFetchingNextPage}>
            다음 문제
            <ChevronRightIcon className="size-4" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between gap-x-2">
      <Button variant="ghost" aria-label="이전 문제" onClick={handlePrevious} disabled={!hasPrevious}>
        <ChevronLeftIcon className="size-4" />
      </Button>
      <div className="flex-1">{children}</div>
      <Button variant="ghost" aria-label="다음 문제" onClick={handleNext} disabled={!hasNext || isFetchingNextPage}>
        <ChevronRightIcon className="size-4" />
      </Button>
    </div>
  );
}

export function ProblemNavigatorSkeleton({ children }: PropsWithChildren) {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <div className="flex flex-col gap-y-2 flex-1">
        <div className="flex-1">{children}</div>

        <div className="flex items-center justify-between gap-x-2">
          <Button variant="ghost" aria-label="이전 문제" disabled>
            <ChevronLeftIcon className="size-4" />
            이전 문제
          </Button>
          <Button variant="ghost" aria-label="다음 문제" disabled>
            다음 문제
            <ChevronRightIcon className="size-4" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between gap-x-2">
      <Button variant="ghost" aria-label="이전 문제" disabled>
        <ChevronLeftIcon className="size-4" />
      </Button>
      <div className="flex-1">{children}</div>
      <Button variant="ghost" aria-label="다음 문제" disabled>
        <ChevronRightIcon className="size-4" />
      </Button>
    </div>
  );
}
