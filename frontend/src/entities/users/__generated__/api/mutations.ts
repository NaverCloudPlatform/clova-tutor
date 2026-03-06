import type { DefaultError, UseMutationOptions } from '@tanstack/react-query';
import { useMutation } from '@tanstack/react-query';

import type { UserCreateResponseDto, UserUpdateResponseDto } from '@/shared/api/__generated__/dto';
import type { TUsersApiRequestParameters } from './index';
import { usersApi } from './instance';

export const USERS_MUTATION_KEY = {
  POST_USERS: ['users'] as const,
  PATCH_USERS_USERID: ['users', 'userId'] as const,
  DELETE_USERS_USERID: ['users', 'userId'] as const,
} as const;

const mutations = {
  postUsers: () => ({
    mutationFn: ({ payload, kyInstance, options }: TUsersApiRequestParameters['postUsers']) => {
      return usersApi.postUsers({ payload, kyInstance, options });
    },
    mutationKey: USERS_MUTATION_KEY.POST_USERS,
    meta: {
      mutationFnName: 'postUsers',
    },
  }),
  patchUsersByUserId: () => ({
    mutationFn: ({ userId, payload, kyInstance, options }: TUsersApiRequestParameters['patchUsersByUserId']) => {
      return usersApi.patchUsersByUserId({
        userId,
        payload,
        kyInstance,
        options,
      });
    },
    mutationKey: USERS_MUTATION_KEY.PATCH_USERS_USERID,
    meta: {
      mutationFnName: 'patchUsersByUserId',
    },
  }),
  deleteUsersByUserId: () => ({
    mutationFn: ({ userId, kyInstance, options }: TUsersApiRequestParameters['deleteUsersByUserId']) => {
      return usersApi.deleteUsersByUserId({ userId, kyInstance, options });
    },
    mutationKey: USERS_MUTATION_KEY.DELETE_USERS_USERID,
    meta: {
      mutationFnName: 'deleteUsersByUserId',
    },
  }),
};

export { mutations as usersMutations };

/**
 * @tags users
 * @summary Create User
 * @request POST:/users
 */
export const usePostUsersMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<UserCreateResponseDto, DefaultError, TUsersApiRequestParameters['postUsers'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.postUsers(),
    ...options,
  });
};

/**
 * @tags users
 * @summary Patch User
 * @request PATCH:/users/{user_id}
 */
export const usePatchUsersByUserIdMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<UserUpdateResponseDto, DefaultError, TUsersApiRequestParameters['patchUsersByUserId'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.patchUsersByUserId(),
    ...options,
  });
};

/**
 * @tags users
 * @summary Delete User
 * @request DELETE:/users/{user_id}
 */
export const useDeleteUsersByUserIdMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<void, DefaultError, TUsersApiRequestParameters['deleteUsersByUserId'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.deleteUsersByUserId(),
    ...options,
  });
};
