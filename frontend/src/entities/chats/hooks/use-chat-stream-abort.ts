/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { type DefaultError, type MutationState, useMutationState } from '@tanstack/react-query';
import { CHATS_MUTATION_KEY } from '../__generated__/api/mutations';
import type { StreamMutationParams } from '../types/stream-mutation';

type TResult = MutationState<unknown, DefaultError, StreamMutationParams>;

type UseChatStreamAbortParams = {
  chatId: number;
};

export function useChatStreamAbort(params: UseChatStreamAbortParams) {
  const { chatId } = params;

  /**
   * mutation의 이종성으로 인해 filter 인자의 타입은 추론 불가능함.
   * @see https://github.com/TanStack/query/discussions/6096#discussioncomment-11810705
   */
  const data = useMutationState<TResult>({
    filters: {
      exact: true,
      mutationKey: CHATS_MUTATION_KEY.POST_CHATS_CHATID_MESSAGES,
      predicate: (mutation) => {
        const variables = mutation.state.variables as StreamMutationParams | undefined;

        if (!variables || variables.chatId !== chatId) {
          return false;
        }

        if (mutation.state.status !== 'pending') {
          return false;
        }

        return true;
      },
    },
  });

  const abortChatStream = () => {
    if (!data || data.length === 0) return;

    const abortController = data.at(-1)?.variables?.abortController;
    abortController?.abort();
  };

  return {
    abortChatStream,
  };
}
