/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { DefaultError, MutationState } from '@tanstack/react-query';
import { useMutationState } from '@tanstack/react-query';
import { last } from 'es-toolkit';
import { CHATS_MUTATION_KEY } from '@/entities/chats/__generated__/api/mutations';
import type { StreamMutationParams } from '../types/stream-mutation';

type TResult = MutationState<unknown, DefaultError, StreamMutationParams>;

type Props = {
  chatId: number;
};

export function useChatStreamMutationState(props: Props) {
  const { chatId } = props;

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

        return true;
      },
    },
  });

  const isStreaming = data?.some((state) => state?.status === 'pending');
  const lastData = last(data);

  return {
    isStreaming,
    status: lastData?.status,
    variables: lastData?.variables,
    context: lastData?.context as { isCreateChat?: boolean } | undefined,
  };
}
