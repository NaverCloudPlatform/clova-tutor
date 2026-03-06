/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { InfiniteData, UseSuspenseInfiniteQueryOptions } from '@tanstack/react-query';
import { useSuspenseInfiniteQuery } from '@tanstack/react-query';
import type { CursorPaginateResponseProblemBookmarkResponseDto } from '@/shared/api/__generated__/dto';
import { TIME } from '@/shared/constants/time';
import type { TProblemBookmarksApiRequestParameters } from '../../__generated__/api';
import { problemBookmarksApi } from '../../__generated__/api/instance';
import { problemBookmarksQueryKeys } from '../../__generated__/api/queries';

export const useGetProblemBookmarksInfiniteSuspenseQuery = (
  requestArgs: TProblemBookmarksApiRequestParameters['getProblemBookmarks'],
  options?: Omit<
    UseSuspenseInfiniteQueryOptions<
      CursorPaginateResponseProblemBookmarkResponseDto,
      Error,
      InfiniteData<CursorPaginateResponseProblemBookmarkResponseDto, string | undefined>,
      readonly unknown[],
      string | undefined
    >,
    'queryKey' | 'queryFn' | 'getNextPageParam' | 'initialPageParam'
  >,
) => {
  return useSuspenseInfiniteQuery({
    queryKey: problemBookmarksQueryKeys.getProblemBookmarks.queryKey(requestArgs.params),
    queryFn: ({ pageParam }) => {
      return problemBookmarksApi.getProblemBookmarks({
        ...requestArgs,
        params: {
          ...requestArgs.params,
          cursor: typeof pageParam === 'string' ? pageParam : undefined,
        },
      });
    },
    getNextPageParam: (lastPage) => {
      return lastPage.next_cursor;
    },
    initialPageParam: undefined as string | undefined,
    staleTime: TIME.MINUTE * 5,
    ...options,
  });
};
