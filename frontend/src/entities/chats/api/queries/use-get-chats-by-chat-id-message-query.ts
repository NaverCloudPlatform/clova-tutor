/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { type queryOptions, useSuspenseQuery } from '@tanstack/react-query';
import type { MessageListResponseDto } from '@/shared/api/__generated__/dto';
import { chatsQueries, type chatsQueryKeys } from '../../__generated__/api/queries';
import { useChatStreamMutationState } from '../../hooks/use-chat-stream-mutation-state';

type GetMessagesQueryKey = ReturnType<typeof chatsQueryKeys.getChatsByChatIdMessages.queryKey>;
type GetMessagesOptions<TSelected = MessageListResponseDto> = Omit<
  Parameters<typeof queryOptions<MessageListResponseDto, Error, TSelected, GetMessagesQueryKey>>[0],
  'queryKey' | 'queryFn'
>;

export const useGetChatsByChatIdMessagesSuspenseQuery = <TSelected = MessageListResponseDto>(
  requestArgs: Parameters<typeof chatsQueries.getChatsByChatIdMessages>[0],
  options?: GetMessagesOptions<TSelected>,
) => {
  const { isStreaming } = useChatStreamMutationState({
    chatId: requestArgs.chatId,
  });

  /**
   * 스트리밍 중 refetch 시 클라이언트의 임시 응답 데이터가 유실되어
   * 스트리밍/로딩 UI 오작동 발생 → 스트리밍 중에는 refetch 비활성화
   */
  return useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdMessages(requestArgs),
    ...options,
    select: options?.select,
    staleTime: Number.POSITIVE_INFINITY,
    gcTime: Number.POSITIVE_INFINITY,
    refetchOnWindowFocus: !isStreaming,
    refetchOnMount: !isStreaming,
    refetchOnReconnect: !isStreaming,
  });
};
