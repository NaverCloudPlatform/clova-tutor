/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { InfiniteData, UseSuspenseInfiniteQueryOptions } from '@tanstack/react-query';
import { useSuspenseInfiniteQuery } from '@tanstack/react-query';
import type { CursorPaginateResponseChatResponseDto } from '@/shared/api/__generated__/dto';
import type { TChatsApiRequestParameters } from '../../__generated__/api';
import { chatsApi } from '../../__generated__/api/instance';
import { chatsQueryKeys } from '../../__generated__/api/queries';

export const useGetChatsInfiniteSuspenseQuery = (
  requestArgs: TChatsApiRequestParameters['getChats'],
  options?: Omit<
    UseSuspenseInfiniteQueryOptions<
      CursorPaginateResponseChatResponseDto,
      Error,
      InfiniteData<CursorPaginateResponseChatResponseDto, string | undefined>,
      readonly unknown[],
      string | undefined
    >,
    'queryKey' | 'queryFn' | 'getNextPageParam' | 'initialPageParam'
  >,
) => {
  return useSuspenseInfiniteQuery({
    queryKey: chatsQueryKeys.getChats.queryKey(requestArgs.params),
    queryFn: ({ pageParam }) => {
      return chatsApi.getChats({
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
    ...options,
  });
};
