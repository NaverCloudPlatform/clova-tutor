import { queryOptions } from '@tanstack/react-query';

import type { TProblemsApiRequestParameters } from './index';
import { problemsApi } from './instance';

const baseKey = 'problems';

const queryKeys = {
  getProblemsByProblemId: {
    rootKey: [baseKey, 'getProblemsByProblemId'],
    queryKey: (problemId: string) => [
      ...queryKeys.getProblemsByProblemId.rootKey,
      ...(problemId != null ? [problemId] : []),
    ],
  },
};

const queries = {
  /**
   * @tags problems
   * @summary Get Problem
   * @request GET:/problems/{problem_id}*
   */
  getProblemsByProblemId: ({
    problemId,
    kyInstance,
    options,
  }: TProblemsApiRequestParameters['getProblemsByProblemId']) =>
    queryOptions({
      queryKey: queryKeys.getProblemsByProblemId.queryKey(problemId),
      queryFn: () => problemsApi.getProblemsByProblemId({ problemId, kyInstance, options }),
    }),
};

export { baseKey as problemsBaseKey, queries as problemsQueries, queryKeys as problemsQueryKeys };
