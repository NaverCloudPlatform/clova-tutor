import type { KyInstance, Options } from 'ky';

import type { GoalCreateRequestBodyDto, GoalResponseDto } from '@/shared/api/__generated__/dto';
import { goalCreateRequestBodyDtoSchema, goalResponseDtoSchema } from '@/shared/api/__generated__/schema';
import { validateSchema } from '@/shared/api/__generated__/utils';

export class GoalsApi {
  private readonly instance: KyInstance;

  constructor(instance: KyInstance) {
    this.instance = instance;
  }

  /**
   * @tags goals
   * @summary Create Goal
   * @request POST:/goals
   */
  async postGoals({ payload, kyInstance, options }: TGoalsApiRequestParameters['postGoals']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(goalCreateRequestBodyDtoSchema, payload);

    const response = await instance
      .post<GoalResponseDto>(`goals`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(goalResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags goals
   * @summary Delete Goal
   * @request DELETE:/goals/{goal_id}
   */
  async deleteGoalsByGoalId({ goalId, kyInstance, options }: TGoalsApiRequestParameters['deleteGoalsByGoalId']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .delete<void>(`goals/${goalId}`, {
        ...options,
      })
      .json();

    return response;
  }
}

export type TGoalsApiRequestParameters = {
  postGoals: {
    payload: GoalCreateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  deleteGoalsByGoalId: {
    goalId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
};
