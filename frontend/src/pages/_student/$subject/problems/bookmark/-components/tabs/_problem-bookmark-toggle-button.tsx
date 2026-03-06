/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { useSearch } from '@tanstack/react-router';
import { BookmarkIcon } from 'lucide-react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { usePatchProblemBookmarksMutation } from '@/entities/problem-bookmarks/__generated__/api/mutations';
import { problemBookmarksQueries } from '@/entities/problem-bookmarks/__generated__/api/queries';
import { withErrorBoundary } from '@/packages/error-boundary';
import type { ProblemBookmarkCreateRequestBodyDto, ProblemBookmarkResponseDto } from '@/shared/api/__generated__/dto';
import { Toggle } from '@/shared/ui/toggle';
import { PROBLEM_BOOKMARK_LIST_PAGE_SIZE } from '../../-constants/common';

type ProblemBookmarkToggleButtonProps = {
  problemId: ProblemBookmarkCreateRequestBodyDto['problem_id'];
  chatId: ProblemBookmarkCreateRequestBodyDto['chat_id'];
  bookmarkedAt: ProblemBookmarkResponseDto['bookmarked_at'];
};

const ProblemBookmarkToggleButtonInner = ({ problemId, chatId, bookmarkedAt }: ProblemBookmarkToggleButtonProps) => {
  const queryClient = useQueryClient();
  const { status } = useSearch({ from: '/_student/$subject/problems/bookmark/' });
  const { subject } = useSubject();
  const { data: isBookmarked } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      problemId: problemId,
      chatId: chatId,
    }),
    select: (data) => data.is_bookmarked,
  });
  const { mutate: createProblemBookmark } = usePatchProblemBookmarksMutation({
    onMutate: () => {
      const bookmarkedProblem = queryClient.getQueryData(
        problemBookmarksQueries.getProblemBookmarks({
          params: {
            subject,
            status,
            size: PROBLEM_BOOKMARK_LIST_PAGE_SIZE,
          },
        }).queryKey,
      );

      return bookmarkedProblem;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: chatsQueries.getChatsByChatIdProblemsByProblemId({ chatId, problemId }).queryKey,
      });
    },
    onSettled: (_, error, __, context) => {
      if (error || !context) {
        return;
      }

      queryClient.setQueryData(
        problemBookmarksQueries.getProblemBookmarks({
          params: {
            subject,
            status,
            size: PROBLEM_BOOKMARK_LIST_PAGE_SIZE,
          },
        }).queryKey,
        context,
      );
    },
    meta: {
      disableGlobalInvalidation: true,
    },
  });

  const handleSaveProblemBookmark = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    createProblemBookmark({
      payload: {
        chat_id: chatId,
        problem_id: problemId,
        is_bookmarked: !isBookmarked,
        bookmarked_at: bookmarkedAt,
      },
    });
  };

  return (
    <Toggle
      aria-label="toggle problem bookmark"
      size="sm"
      variant="outline"
      className="data-[state=on]:bg-background data-[state=on]:*:[svg]:fill-blue-500 data-[state=on]:*:[svg]:stroke-blue-500 cursor-pointer"
      pressed={isBookmarked}
      onClick={handleSaveProblemBookmark}
    >
      <BookmarkIcon />
    </Toggle>
  );
};

export const ProblemBookmarkToggleButton = withErrorBoundary(ProblemBookmarkToggleButtonInner, {
  fallback: <ProblemBookmarkToggleButtonSkeleton />,
});

export function ProblemBookmarkToggleButtonSkeleton() {
  return (
    <Toggle
      aria-label="toggle problem bookmark"
      size="sm"
      variant="outline"
      className="data-[state=on]:bg-background data-[state=on]:*:[svg]:fill-blue-500 data-[state=on]:*:[svg]:stroke-blue-500"
      pressed={false}
      disabled
    >
      <BookmarkIcon />
    </Toggle>
  );
}
