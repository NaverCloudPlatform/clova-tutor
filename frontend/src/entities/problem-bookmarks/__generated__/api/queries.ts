import { queryOptions } from '@tanstack/react-query';

import type { GetProblemBookmarksProblemBookmarksGetQueryParams } from '@/shared/api/__generated__/dto';
import type { TProblemBookmarksApiRequestParameters } from './index';
import { problemBookmarksApi } from './instance';

const baseKey = 'problemBookmarks';

const queryKeys = {
  getProblemBookmarks: {
    rootKey: [baseKey, 'getProblemBookmarks'],
    queryKey: (params: GetProblemBookmarksProblemBookmarksGetQueryParams) => [
      ...queryKeys.getProblemBookmarks.rootKey,
      ...(params ? [params] : []),
    ],
  },
  getProblemBookmarksProblemByProblemIdCheck: {
    rootKey: [baseKey, 'getProblemBookmarksProblemByProblemIdCheck'],
    queryKey: (problemId: string) => [
      ...queryKeys.getProblemBookmarksProblemByProblemIdCheck.rootKey,
      ...(problemId != null ? [problemId] : []),
    ],
  },
};

const queries = {
  /**
   * @tags problem-bookmarks
   * @summary Get Problem Bookmarks
   * @request GET:/problem-bookmarks*
   */
  getProblemBookmarks: ({
    params,
    kyInstance,
    options,
  }: TProblemBookmarksApiRequestParameters['getProblemBookmarks']) =>
    queryOptions({
      queryKey: queryKeys.getProblemBookmarks.queryKey(params),
      queryFn: () =>
        problemBookmarksApi.getProblemBookmarks({
          params,
          kyInstance,
          options,
        }),
    }),

  /**
   * @tags problem-bookmarks
   * @summary Check Problem Bookmark Duplicate
   * @request GET:/problem-bookmarks/problem/{problem_id}/check*
   */
  getProblemBookmarksProblemByProblemIdCheck: ({
    problemId,
    kyInstance,
    options,
  }: TProblemBookmarksApiRequestParameters['getProblemBookmarksProblemByProblemIdCheck']) =>
    queryOptions({
      queryKey: queryKeys.getProblemBookmarksProblemByProblemIdCheck.queryKey(problemId),
      queryFn: () =>
        problemBookmarksApi.getProblemBookmarksProblemByProblemIdCheck({
          problemId,
          kyInstance,
          options,
        }),
    }),
};

export {
  baseKey as problemBookmarksBaseKey,
  queries as problemBookmarksQueries,
  queryKeys as problemBookmarksQueryKeys,
};
