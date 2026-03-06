import type { KyInstance, Options } from 'ky';

import type {
  CreateProblemsProblemsPostHeaders,
  ProblemCreateRequestBodyDto,
  ProblemCreateResponseDto,
  ProblemResponseDto,
} from '@/shared/api/__generated__/dto';
import {
  problemCreateRequestBodyDtoSchema,
  problemCreateResponseDtoSchema,
  problemResponseDtoSchema,
} from '@/shared/api/__generated__/schema';
import { validateSchema } from '@/shared/api/__generated__/utils';

export class ProblemsApi {
  private readonly instance: KyInstance;

  constructor(instance: KyInstance) {
    this.instance = instance;
  }

  /**
   * @tags problems
   * @summary Get Problem
   * @request GET:/problems/{problem_id}
   */
  async getProblemsByProblemId({
    problemId,
    kyInstance,
    options,
  }: TProblemsApiRequestParameters['getProblemsByProblemId']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<ProblemResponseDto>(`problems/${problemId}`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(problemResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags problems
   * @summary Create Problems
   * @request POST:/problems
   */
  async postProblems({ payload, kyInstance, options }: TProblemsApiRequestParameters['postProblems']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(problemCreateRequestBodyDtoSchema, payload);

    const response = await instance
      .post<ProblemCreateResponseDto>(`problems`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(problemCreateResponseDtoSchema, response);
    return validateResponse;
  }
}

export type TProblemsApiRequestParameters = {
  getProblemsByProblemId: {
    problemId: string;
    kyInstance?: KyInstance;
    options?: Options;
  };
  postProblems: {
    payload: ProblemCreateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Omit<Options, 'headers'> & {
      headers: CreateProblemsProblemsPostHeaders;
    };
  };
};
