import type { DefaultError, UseMutationOptions } from '@tanstack/react-query';
import { useMutation } from '@tanstack/react-query';

import type { ProblemBookmarkCreateResponseDto } from '@/shared/api/__generated__/dto';
import type { TProblemBookmarksApiRequestParameters } from './index';
import { problemBookmarksApi } from './instance';

export const PROBLEMBOOKMARKS_MUTATION_KEY = {
  PATCH_PROBLEM_BOOKMARKS: ['problem-bookmarks'] as const,
} as const;

const mutations = {
  patchProblemBookmarks: () => ({
    mutationFn: ({ payload, kyInstance, options }: TProblemBookmarksApiRequestParameters['patchProblemBookmarks']) => {
      return problemBookmarksApi.patchProblemBookmarks({
        payload,
        kyInstance,
        options,
      });
    },
    mutationKey: PROBLEMBOOKMARKS_MUTATION_KEY.PATCH_PROBLEM_BOOKMARKS,
    meta: {
      mutationFnName: 'patchProblemBookmarks',
    },
  }),
};

export { mutations as problemBookmarksMutations };

/**
 * @tags problem-bookmarks
 * @summary Bookmark Problem
 * @request PATCH:/problem-bookmarks
 */
export const usePatchProblemBookmarksMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<
      ProblemBookmarkCreateResponseDto,
      DefaultError,
      TProblemBookmarksApiRequestParameters['patchProblemBookmarks'],
      TContext
    >,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.patchProblemBookmarks(),
    ...options,
  });
};
