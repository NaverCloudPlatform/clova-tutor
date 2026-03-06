/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import { chatsApi } from '../__generated__/api/instance';
import { CHATS_MUTATION_KEY } from '../__generated__/api/mutations';
import { chatsQueries } from '../__generated__/api/queries';
import { ChatNotificationService } from '../service/chat-notification-service';
import { ChatQueryCacheService } from '../service/chat-query-cache-service';
import type { MessageDeltaData } from '../types/stream';
import type { StreamMutationParams, UseChatStreamMutationCallbacks } from '../types/stream-mutation';
import { StreamingBuffer } from '../utils/streaming-buffer';
import { useSubject } from './use-subject';

export function useChatStreamResumeMutation() {
  const queryClient = useQueryClient();
  const deleteAll = useRichEditorStore((state) => state.deleteAll);
  const { subject } = useSubject();

  const mutation = useMutation({
    mutationFn: async ({
      chatId,
      callbacks,
      abortController,
    }: Pick<StreamMutationParams, 'chatId' | 'callbacks' | 'abortController'>) => {
      const chatQueryCacheService = new ChatQueryCacheService(queryClient, chatId);
      const chatNotificationService = new ChatNotificationService(chatId, subject);

      chatQueryCacheService.initializeStreamingMessagesResume();
      callbacks?.message_send?.();

      return new Promise<void>((resolve, reject) => {
        const streamingBuffer = new StreamingBuffer<MessageDeltaData>({
          onTokenUpdate: (token) => chatQueryCacheService.updateAssistantMessageTextContent(token),
          onAllTokensProcessed: () => resolve(),
          interval: 15,
        });

        abortController?.signal.addEventListener(
          'abort',
          () => {
            streamingBuffer.abort();
            resolve();
          },
          {
            once: true,
          },
        );

        chatsApi
          .postChatsByChatIdResume({
            chatId,
            callbacks: {
              message_start: (data) => {
                chatQueryCacheService.updateAssistantMessage(data);
                callbacks?.message_start?.(data);
              },
              message_delta: (data) => {
                streamingBuffer.addToken(data);
                callbacks?.message_delta?.(data);
              },
              message_end: async (finalData: ChatMessageResponseDto) => {
                streamingBuffer.completeStream();
                streamingBuffer.flush(() => {
                  chatQueryCacheService.updateFinalAssistantMessage(finalData);
                  chatNotificationService.showNotification(finalData);

                  const isTitleEmpty =
                    queryClient.getQueryData(chatsQueries.getChatsByChatId({ chatId }).queryKey)?.title === '';

                  if (isTitleEmpty) {
                    queryClient.invalidateQueries({
                      ...chatsQueries.getChats({ params: undefined }).queryKey,
                      exact: false,
                    });
                  }

                  queryClient.invalidateQueries(chatsQueries.getChatsByChatIdMessages({ chatId }));
                  callbacks?.message_end?.(finalData);
                });
              },
              error: (error) => {
                streamingBuffer.flush(() => {
                  callbacks?.error?.(error);
                  reject(error);
                });
              },
            },
            options: {
              signal: abortController?.signal,
            },
          })
          .catch((error) => {
            chatQueryCacheService.rollbackStreamingMessages();
            reject(error);
          });
      });
    },
    meta: {
      disableGlobalInvalidation: true,
    },
    mutationKey: CHATS_MUTATION_KEY.POST_CHATS_CHATID_MESSAGES,
  });

  const streamResumeMutate = (chatId: number, callbacks?: UseChatStreamMutationCallbacks) => {
    deleteAll();

    const abortController = new AbortController();

    return mutation.mutate({
      chatId,
      callbacks,
      abortController,
    });
  };

  return {
    streamResumeMutate,
  };
}
