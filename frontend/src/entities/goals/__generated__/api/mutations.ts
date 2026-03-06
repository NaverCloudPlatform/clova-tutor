import type { DefaultError, UseMutationOptions } from '@tanstack/react-query';
import { useMutation } from '@tanstack/react-query';

import type { GoalResponseDto } from '@/shared/api/__generated__/dto';
import type { TGoalsApiRequestParameters } from './index';
import { goalsApi } from './instance';

export const GOALS_MUTATION_KEY = {
  POST_GOALS: ['goals'] as const,
  DELETE_GOALS_GOALID: ['goals', 'goalId'] as const,
} as const;

const mutations = {
  postGoals: () => ({
    mutationFn: ({ payload, kyInstance, options }: TGoalsApiRequestParameters['postGoals']) => {
      return goalsApi.postGoals({ payload, kyInstance, options });
    },
    mutationKey: GOALS_MUTATION_KEY.POST_GOALS,
    meta: {
      mutationFnName: 'postGoals',
    },
  }),
  deleteGoalsByGoalId: () => ({
    mutationFn: ({ goalId, kyInstance, options }: TGoalsApiRequestParameters['deleteGoalsByGoalId']) => {
      return goalsApi.deleteGoalsByGoalId({ goalId, kyInstance, options });
    },
    mutationKey: GOALS_MUTATION_KEY.DELETE_GOALS_GOALID,
    meta: {
      mutationFnName: 'deleteGoalsByGoalId',
    },
  }),
};

export { mutations as goalsMutations };

/**
 * @tags goals
 * @summary Create Goal
 * @request POST:/goals
 */
export const usePostGoalsMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<GoalResponseDto, DefaultError, TGoalsApiRequestParameters['postGoals'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.postGoals(),
    ...options,
  });
};

/**
 * @tags goals
 * @summary Delete Goal
 * @request DELETE:/goals/{goal_id}
 */
export const useDeleteGoalsByGoalIdMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<void, DefaultError, TGoalsApiRequestParameters['deleteGoalsByGoalId'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.deleteGoalsByGoalId(),
    ...options,
  });
};
