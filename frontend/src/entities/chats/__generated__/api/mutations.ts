import type { DefaultError, UseMutationOptions } from '@tanstack/react-query';
import { useMutation } from '@tanstack/react-query';

import type {
  ChatMessageStopResponseDto,
  ChatProblemSubmitResponseDto,
  ChatResponseDto,
} from '@/shared/api/__generated__/dto';
import type { TChatsApiRequestParameters } from './index';
import { chatsApi } from './instance';

export const CHATS_MUTATION_KEY = {
  POST_CHATS: ['chats'] as const,
  PATCH_CHATS_CHATID: ['chats', 'chatId'] as const,
  DELETE_CHATS_CHATID: ['chats', 'chatId'] as const,
  POST_CHATS_CHATID_RESUME: ['chats', 'chatId', 'resume'] as const,
  POST_CHATS_CHATID_STOP_CONVERSATION: ['chats', 'chatId', 'stop-conversation'] as const,
  POST_CHATS_CHATID_MESSAGES: ['chats', 'chatId', 'messages'] as const,
  POST_CHATS_CHATID_PROBLEMS_PROBLEMID_SUBMIT: ['chats', 'chatId', 'problems', 'problemId', 'submit'] as const,
} as const;

const mutations = {
  postChats: () => ({
    mutationFn: ({ payload, kyInstance, options }: TChatsApiRequestParameters['postChats']) => {
      return chatsApi.postChats({ payload, kyInstance, options });
    },
    mutationKey: CHATS_MUTATION_KEY.POST_CHATS,
    meta: {
      mutationFnName: 'postChats',
    },
  }),
  patchChatsByChatId: () => ({
    mutationFn: ({ chatId, payload, kyInstance, options }: TChatsApiRequestParameters['patchChatsByChatId']) => {
      return chatsApi.patchChatsByChatId({
        chatId,
        payload,
        kyInstance,
        options,
      });
    },
    mutationKey: CHATS_MUTATION_KEY.PATCH_CHATS_CHATID,
    meta: {
      mutationFnName: 'patchChatsByChatId',
    },
  }),
  deleteChatsByChatId: () => ({
    mutationFn: ({ chatId, kyInstance, options }: TChatsApiRequestParameters['deleteChatsByChatId']) => {
      return chatsApi.deleteChatsByChatId({ chatId, kyInstance, options });
    },
    mutationKey: CHATS_MUTATION_KEY.DELETE_CHATS_CHATID,
    meta: {
      mutationFnName: 'deleteChatsByChatId',
    },
  }),
  postChatsByChatIdStopConversation: () => ({
    mutationFn: ({ chatId, kyInstance, options }: TChatsApiRequestParameters['postChatsByChatIdStopConversation']) => {
      return chatsApi.postChatsByChatIdStopConversation({
        chatId,
        kyInstance,
        options,
      });
    },
    mutationKey: CHATS_MUTATION_KEY.POST_CHATS_CHATID_STOP_CONVERSATION,
    meta: {
      mutationFnName: 'postChatsByChatIdStopConversation',
    },
  }),
  postChatsByChatIdProblemsByProblemIdSubmit: () => ({
    mutationFn: ({
      chatId,
      problemId,
      payload,
      kyInstance,
      options,
    }: TChatsApiRequestParameters['postChatsByChatIdProblemsByProblemIdSubmit']) => {
      return chatsApi.postChatsByChatIdProblemsByProblemIdSubmit({
        chatId,
        problemId,
        payload,
        kyInstance,
        options,
      });
    },
    mutationKey: CHATS_MUTATION_KEY.POST_CHATS_CHATID_PROBLEMS_PROBLEMID_SUBMIT,
    meta: {
      mutationFnName: 'postChatsByChatIdProblemsByProblemIdSubmit',
    },
  }),
};

export { mutations as chatsMutations };

/**
 * @tags chats
 * @summary Create Chat
 * @request POST:/chats
 */
export const usePostChatsMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<ChatResponseDto, DefaultError, TChatsApiRequestParameters['postChats'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.postChats(),
    ...options,
  });
};

/**
 * @tags chats
 * @summary Update Chat Title
 * @request PATCH:/chats/{chat_id}
 */
export const usePatchChatsByChatIdMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<ChatResponseDto, DefaultError, TChatsApiRequestParameters['patchChatsByChatId'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.patchChatsByChatId(),
    ...options,
  });
};

/**
 * @tags chats
 * @summary Delete Chat
 * @request DELETE:/chats/{chat_id}
 */
export const useDeleteChatsByChatIdMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<void, DefaultError, TChatsApiRequestParameters['deleteChatsByChatId'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.deleteChatsByChatId(),
    ...options,
  });
};

/**
 * @tags chats
 * @summary Stop Stream
 * @request POST:/chats/{chat_id}/stop-conversation
 */
export const usePostChatsByChatIdStopConversationMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<
      ChatMessageStopResponseDto,
      DefaultError,
      TChatsApiRequestParameters['postChatsByChatIdStopConversation'],
      TContext
    >,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.postChatsByChatIdStopConversation(),
    ...options,
  });
};

/**
 * @tags chats
 * @summary Submit Chat Problem
 * @request POST:/chats/{chat_id}/problems/{problem_id}/submit
 */
export const usePostChatsByChatIdProblemsByProblemIdSubmitMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<
      ChatProblemSubmitResponseDto,
      DefaultError,
      TChatsApiRequestParameters['postChatsByChatIdProblemsByProblemIdSubmit'],
      TContext
    >,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.postChatsByChatIdProblemsByProblemIdSubmit(),
    ...options,
  });
};
