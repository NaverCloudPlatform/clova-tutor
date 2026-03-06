/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { type MutationFilters, useMutationState } from '@tanstack/react-query';
import type { ChatProblemSubmitResponseDto } from '@/shared/api/__generated__/dto';
import { isChatProblemSubmitResponseDto } from '@/shared/api/__generated__/type-guards';
import type { TChatsApiRequestParameters } from '../__generated__/api';
import { CHATS_MUTATION_KEY } from '../__generated__/api/mutations';

type UseChatProblemSubmitMutationStateParams<TResult> = Pick<
  TChatsApiRequestParameters['postChatsByChatIdProblemsByProblemIdSubmit'],
  'chatId'
> & {
  status?: MutationFilters['status'];
  select?: (data: ChatProblemSubmitResponseDto) => TResult | null;
};

export function useChatProblemSubmitMutationState<TResult = ChatProblemSubmitResponseDto>(
  props: UseChatProblemSubmitMutationStateParams<TResult>,
) {
  const { chatId, select } = props;

  /**
   * mutation의 이종성으로 인해 filter 인자의 타입은 추론 불가능함.
   * @see https://github.com/TanStack/query/discussions/6096#discussioncomment-11810705
   */
  const data = useMutationState({
    filters: {
      exact: true,
      mutationKey: CHATS_MUTATION_KEY.POST_CHATS_CHATID_PROBLEMS_PROBLEMID_SUBMIT,
      predicate: (mutation) => {
        const variables = mutation.state.variables as
          | TChatsApiRequestParameters['postChatsByChatIdProblemsByProblemIdSubmit']
          | undefined;

        if (!variables || variables.chatId !== chatId) {
          return false;
        }

        return true;
      },
      status: props.status,
    },
    select: (data) => {
      if (!isChatProblemSubmitResponseDto(data.state.data)) {
        return null;
      }

      return select?.(data.state.data) ?? data.state.data;
    },
  });

  return data;
}
