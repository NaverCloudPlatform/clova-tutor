/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSearch } from '@tanstack/react-router';
import { useGetProblemBookmarksInfiniteSuspenseQuery } from '@/entities/problem-bookmarks/api/queries/use-get-problem-bookmarks-infinite-query';
import type { SubjectEnumDto } from '@/shared/api/__generated__/dto';
import { useInfiniteScroll } from '@/shared/hooks/use-infinite-scroll';
import { Skeleton } from '@/shared/ui/skeleton';
import { PROBLEM_BOOKMARK_LIST_PAGE_SIZE } from '../../-constants/common';
import { ProblemBookmarkItem } from './_problem-bookmark-item';

type ProblemBookmarkListProps = {
  subject: SubjectEnumDto;
};

export function ProblemBookmarkList({ subject }: ProblemBookmarkListProps) {
  const { status } = useSearch({ from: '/_student/$subject/problems/bookmark/' });
  const {
    data: bookmarkedProblems,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useGetProblemBookmarksInfiniteSuspenseQuery({
    params: {
      subject: subject,
      status,
      size: PROBLEM_BOOKMARK_LIST_PAGE_SIZE,
    },
  });
  const { observerRootRef, lastElementRef } = useInfiniteScroll({
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  });

  if (bookmarkedProblems.pages.every((page) => page.items.length === 0)) {
    return (
      <div className="flex flex-col gap-y-4 w-full items-center justify-center py-12">
        <div className="text-sm text-muted-foreground">저장된 문제가 없습니다.</div>
      </div>
    );
  }

  return (
    <div ref={observerRootRef} className="flex flex-col">
      <div className="grid grid-cols-1 @sm:grid-cols-2 @2xl:grid-cols-3 gap-4">
        {bookmarkedProblems.pages.map((page) =>
          page.items.map((problem) => (
            <ProblemBookmarkItem
              key={`${problem.problem.problem_info.id}-${problem.chat.id}`}
              bookmarkedProblem={problem}
            />
          )),
        )}
      </div>

      <div ref={lastElementRef} />

      {isFetchingNextPage && (
        <div className="flex items-center justify-center py-4">
          <div className="text-sm text-gray-500">로딩 중...</div>
        </div>
      )}
    </div>
  );
}

export function ProblemBookmarkListSkeleton() {
  return (
    <div className="grid grid-cols-1 @sm:grid-cols-2 @2xl:grid-cols-3 gap-4">
      {Array.from({ length: 12 }).map((_, index) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: 스켈레톤 컴포넌트 인덱스 키
        <Skeleton key={index} className="h-80 w-full" />
      ))}
    </div>
  );
}
