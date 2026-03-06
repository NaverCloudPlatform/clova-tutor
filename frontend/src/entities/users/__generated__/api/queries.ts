import { queryOptions } from '@tanstack/react-query';

import type { TUsersApiRequestParameters } from './index';
import { usersApi } from './instance';

const baseKey = 'users';

const queryKeys = {
  getUsers: {
    rootKey: [baseKey, 'getUsers'],
    queryKey: () => [...queryKeys.getUsers.rootKey],
  },
  getUsersByUserId: {
    rootKey: [baseKey, 'getUsersByUserId'],
    queryKey: (userId: string) => [...queryKeys.getUsersByUserId.rootKey, ...(userId != null ? [userId] : [])],
  },
};

const queries = {
  /**
   * @tags users
   * @summary Get Users
   * @request GET:/users*
   */
  getUsers: ({ kyInstance, options }: TUsersApiRequestParameters['getUsers']) =>
    queryOptions({
      queryKey: queryKeys.getUsers.queryKey(),
      queryFn: () => usersApi.getUsers({ kyInstance, options }),
      staleTime: Number.POSITIVE_INFINITY,
      gcTime: Number.POSITIVE_INFINITY,
    }),

  /**
   * @tags users
   * @summary Get User
   * @request GET:/users/{user_id}*
   */
  getUsersByUserId: ({ userId, kyInstance, options }: TUsersApiRequestParameters['getUsersByUserId']) =>
    queryOptions({
      queryKey: queryKeys.getUsersByUserId.queryKey(userId),
      queryFn: () => usersApi.getUsersByUserId({ userId, kyInstance, options }),
      staleTime: Number.POSITIVE_INFINITY,
      gcTime: Number.POSITIVE_INFINITY,
    }),
};

export { baseKey as usersBaseKey, queries as usersQueries, queryKeys as usersQueryKeys };
