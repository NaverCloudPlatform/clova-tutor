import type { DefaultError, UseMutationOptions } from '@tanstack/react-query';
import { useMutation } from '@tanstack/react-query';

import type { ProblemCreateResponseDto } from '@/shared/api/__generated__/dto';
import type { TProblemsApiRequestParameters } from './index';
import { problemsApi } from './instance';

export const PROBLEMS_MUTATION_KEY = {
  POST_PROBLEMS: ['problems'] as const,
} as const;

const mutations = {
  postProblems: () => ({
    mutationFn: ({ payload, kyInstance, options }: TProblemsApiRequestParameters['postProblems']) => {
      return problemsApi.postProblems({ payload, kyInstance, options });
    },
    mutationKey: PROBLEMS_MUTATION_KEY.POST_PROBLEMS,
    meta: {
      mutationFnName: 'postProblems',
    },
  }),
};

export { mutations as problemsMutations };

/**
 * @tags problems
 * @summary Create Problems
 * @request POST:/problems
 */
export const usePostProblemsMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<ProblemCreateResponseDto, DefaultError, TProblemsApiRequestParameters['postProblems'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.postProblems(),
    ...options,
  });
};
