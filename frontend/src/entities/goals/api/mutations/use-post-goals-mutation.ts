/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient } from '@tanstack/react-query';
import { produce } from 'immer';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { usePostGoalsMutation as usePostGoalsMutationGenerated } from '../../__generated__/api/mutations';

export const usePostGoalsMutation = (...params: Parameters<typeof usePostGoalsMutationGenerated>) => {
  const queryClient = useQueryClient();

  return usePostGoalsMutationGenerated({
    ...params,
    onSuccess: (data, variables, context) => {
      queryClient.setQueryData(chatsQueries.getChatsByChatId({ chatId: variables.payload.chat_id }).queryKey, (old) => {
        if (!old) return old;

        return produce(old, (draft) => {
          draft.active_goal = data;
          draft.has_active_goal = true;
        });
      });

      params[0]?.onSuccess?.(data, variables, context);
    },
  });
};
