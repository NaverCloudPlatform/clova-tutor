import { queryOptions } from '@tanstack/react-query';

import type { GetChatsChatsGetQueryParams } from '@/shared/api/__generated__/dto';
import type { TChatsApiRequestParameters } from './index';
import { chatsApi } from './instance';

const baseKey = 'chats';

const queryKeys = {
  getChats: {
    rootKey: [baseKey, 'getChats'],
    queryKey: (params?: GetChatsChatsGetQueryParams) => [...queryKeys.getChats.rootKey, ...(params ? [params] : [])],
  },
  getChatsByChatId: {
    rootKey: [baseKey, 'getChatsByChatId'],
    queryKey: (chatId: number) => [...queryKeys.getChatsByChatId.rootKey, ...(chatId != null ? [chatId] : [])],
  },
  getChatsByChatIdStreamStatus: {
    rootKey: [baseKey, 'getChatsByChatIdStreamStatus'],
    queryKey: (chatId: number) => [
      ...queryKeys.getChatsByChatIdStreamStatus.rootKey,
      ...(chatId != null ? [chatId] : []),
    ],
  },
  getChatsByChatIdMessages: {
    rootKey: [baseKey, 'getChatsByChatIdMessages'],
    queryKey: (chatId: number) => [...queryKeys.getChatsByChatIdMessages.rootKey, ...(chatId != null ? [chatId] : [])],
  },
  getChatsByChatIdProblems: {
    rootKey: [baseKey, 'getChatsByChatIdProblems'],
    queryKey: (chatId: number) => [...queryKeys.getChatsByChatIdProblems.rootKey, ...(chatId != null ? [chatId] : [])],
  },
  getChatsByChatIdProblemsByProblemId: {
    rootKey: [baseKey, 'getChatsByChatIdProblemsByProblemId'],
    queryKey: (chatId: number, problemId: string) => [
      ...queryKeys.getChatsByChatIdProblemsByProblemId.rootKey,
      ...(chatId != null ? [chatId] : []),
      ...(problemId != null ? [problemId] : []),
    ],
  },
};

const queries = {
  /**
   * @tags chats
   * @summary Get Chats
   * @request GET:/chats*
   */
  getChats: ({ params, kyInstance, options }: TChatsApiRequestParameters['getChats']) =>
    queryOptions({
      queryKey: queryKeys.getChats.queryKey(params),
      queryFn: () => chatsApi.getChats({ params, kyInstance, options }),
    }),

  /**
   * @tags chats
   * @summary Get Chat
   * @request GET:/chats/{chat_id}*
   */
  getChatsByChatId: ({ chatId, kyInstance, options }: TChatsApiRequestParameters['getChatsByChatId']) =>
    queryOptions({
      queryKey: queryKeys.getChatsByChatId.queryKey(chatId),
      queryFn: () => chatsApi.getChatsByChatId({ chatId, kyInstance, options }),
      staleTime: Number.POSITIVE_INFINITY,
    }),

  /**
   * @tags chats
   * @summary Get Chat Stream Status
   * @request GET:/chats/{chat_id}/stream-status*
   */
  getChatsByChatIdStreamStatus: ({
    chatId,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['getChatsByChatIdStreamStatus']) =>
    queryOptions({
      queryKey: queryKeys.getChatsByChatIdStreamStatus.queryKey(chatId),
      queryFn: () => chatsApi.getChatsByChatIdStreamStatus({ chatId, kyInstance, options }),
    }),

  /**
   * @tags chats
   * @summary Get Messages
   * @request GET:/chats/{chat_id}/messages*
   */
  getChatsByChatIdMessages: ({ chatId, kyInstance, options }: TChatsApiRequestParameters['getChatsByChatIdMessages']) =>
    queryOptions({
      queryKey: queryKeys.getChatsByChatIdMessages.queryKey(chatId),
      queryFn: () => chatsApi.getChatsByChatIdMessages({ chatId, kyInstance, options }),
    }),

  /**
   * @tags chats
   * @summary Get Chat Problems
   * @request GET:/chats/{chat_id}/problems*
   */
  getChatsByChatIdProblems: ({ chatId, kyInstance, options }: TChatsApiRequestParameters['getChatsByChatIdProblems']) =>
    queryOptions({
      queryKey: queryKeys.getChatsByChatIdProblems.queryKey(chatId),
      queryFn: () => chatsApi.getChatsByChatIdProblems({ chatId, kyInstance, options }),
    }),

  /**
   * @tags chats
   * @summary Get Chat Problem
   * @request GET:/chats/{chat_id}/problems/{problem_id}*
   */
  getChatsByChatIdProblemsByProblemId: ({
    chatId,
    problemId,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['getChatsByChatIdProblemsByProblemId']) =>
    queryOptions({
      queryKey: queryKeys.getChatsByChatIdProblemsByProblemId.queryKey(chatId, problemId),
      queryFn: () =>
        chatsApi.getChatsByChatIdProblemsByProblemId({
          chatId,
          problemId,
          kyInstance,
          options,
        }),
    }),
};

export { baseKey as chatsBaseKey, queries as chatsQueries, queryKeys as chatsQueryKeys };
