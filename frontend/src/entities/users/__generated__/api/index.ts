import type { KyInstance, Options } from 'ky';
import { z } from 'zod';

import type {
  UserCreateRequestBodyDto,
  UserCreateResponseDto,
  UserResponseDto,
  UserUpdateRequestBodyDto,
  UserUpdateResponseDto,
} from '@/shared/api/__generated__/dto';
import {
  userCreateRequestBodyDtoSchema,
  userCreateResponseDtoSchema,
  userResponseDtoSchema,
  userUpdateRequestBodyDtoSchema,
  userUpdateResponseDtoSchema,
} from '@/shared/api/__generated__/schema';
import { validateSchema } from '@/shared/api/__generated__/utils';

export class UsersApi {
  private readonly instance: KyInstance;

  constructor(instance: KyInstance) {
    this.instance = instance;
  }

  /**
   * @tags users
   * @summary Get Users
   * @request GET:/users
   */
  async getUsers({ kyInstance, options }: TUsersApiRequestParameters['getUsers'] = {}) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<UserResponseDto[]>(`users`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(z.array(userResponseDtoSchema), response);
    return validateResponse;
  }

  /**
   * @tags users
   * @summary Create User
   * @request POST:/users
   */
  async postUsers({ payload, kyInstance, options }: TUsersApiRequestParameters['postUsers']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(userCreateRequestBodyDtoSchema, payload);

    const response = await instance
      .post<UserCreateResponseDto>(`users`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(userCreateResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags users
   * @summary Get User
   * @request GET:/users/{user_id}
   */
  async getUsersByUserId({ userId, kyInstance, options }: TUsersApiRequestParameters['getUsersByUserId']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<UserResponseDto>(`users/${userId}`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(userResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags users
   * @summary Patch User
   * @request PATCH:/users/{user_id}
   */
  async patchUsersByUserId({ userId, payload, kyInstance, options }: TUsersApiRequestParameters['patchUsersByUserId']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(userUpdateRequestBodyDtoSchema, payload);

    const response = await instance
      .patch<UserUpdateResponseDto>(`users/${userId}`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(userUpdateResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags users
   * @summary Delete User
   * @request DELETE:/users/{user_id}
   */
  async deleteUsersByUserId({ userId, kyInstance, options }: TUsersApiRequestParameters['deleteUsersByUserId']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .delete<void>(`users/${userId}`, {
        ...options,
      })
      .json();

    return response;
  }
}

export type TUsersApiRequestParameters = {
  getUsers: {
    kyInstance?: KyInstance;
    options?: Options;
  };
  postUsers: {
    payload: UserCreateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  getUsersByUserId: {
    userId: string;
    kyInstance?: KyInstance;
    options?: Options;
  };
  patchUsersByUserId: {
    userId: string;
    payload: UserUpdateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  deleteUsersByUserId: {
    userId: string;
    kyInstance?: KyInstance;
    options?: Options;
  };
};
