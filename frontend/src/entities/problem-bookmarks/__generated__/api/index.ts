import type { KyInstance, Options } from 'ky';

import type {
  CursorPaginateResponseProblemBookmarkResponseDto,
  GetProblemBookmarksProblemBookmarksGetQueryParams,
  ProblemBookmarkCheckResponseDto,
  ProblemBookmarkCreateRequestBodyDto,
  ProblemBookmarkCreateResponseDto,
} from '@/shared/api/__generated__/dto';
import {
  cursorPaginateResponseProblemBookmarkResponseDtoSchema,
  problemBookmarkCheckResponseDtoSchema,
  problemBookmarkCreateRequestBodyDtoSchema,
  problemBookmarkCreateResponseDtoSchema,
} from '@/shared/api/__generated__/schema';
import { createSearchParams, validateSchema } from '@/shared/api/__generated__/utils';

export class ProblemBookmarksApi {
  private readonly instance: KyInstance;

  constructor(instance: KyInstance) {
    this.instance = instance;
  }

  /**
   * @tags problem-bookmarks
   * @summary Get Problem Bookmarks
   * @request GET:/problem-bookmarks
   */
  async getProblemBookmarks({
    params,
    kyInstance,
    options,
  }: TProblemBookmarksApiRequestParameters['getProblemBookmarks']) {
    const instance = kyInstance ?? this.instance;

    const urlSearchParams = createSearchParams(params);
    const response = await instance
      .get<CursorPaginateResponseProblemBookmarkResponseDto>(`problem-bookmarks`, {
        searchParams: urlSearchParams,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(cursorPaginateResponseProblemBookmarkResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags problem-bookmarks
   * @summary Bookmark Problem
   * @request PATCH:/problem-bookmarks
   */
  async patchProblemBookmarks({
    payload,
    kyInstance,
    options,
  }: TProblemBookmarksApiRequestParameters['patchProblemBookmarks']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(problemBookmarkCreateRequestBodyDtoSchema, payload);

    const response = await instance
      .patch<ProblemBookmarkCreateResponseDto>(`problem-bookmarks`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(problemBookmarkCreateResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags problem-bookmarks
   * @summary Check Problem Bookmark Duplicate
   * @request GET:/problem-bookmarks/problem/{problem_id}/check
   */
  async getProblemBookmarksProblemByProblemIdCheck({
    problemId,
    kyInstance,
    options,
  }: TProblemBookmarksApiRequestParameters['getProblemBookmarksProblemByProblemIdCheck']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<ProblemBookmarkCheckResponseDto>(`problem-bookmarks/problem/${problemId}/check`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(problemBookmarkCheckResponseDtoSchema, response);
    return validateResponse;
  }
}

export type TProblemBookmarksApiRequestParameters = {
  getProblemBookmarks: {
    params: GetProblemBookmarksProblemBookmarksGetQueryParams;
    kyInstance?: KyInstance;
    options?: Options;
  };
  patchProblemBookmarks: {
    payload: ProblemBookmarkCreateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  getProblemBookmarksProblemByProblemIdCheck: {
    problemId: string;
    kyInstance?: KyInstance;
    options?: Options;
  };
};
