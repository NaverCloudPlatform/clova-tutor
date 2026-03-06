/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient } from '@tanstack/react-query';
import { useParams } from '@tanstack/react-router';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useChatStreamMutation } from '@/entities/chats/hooks/use-chat-stream';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { ChatAlert } from '@/entities/chats/ui/chat-alert';
import { useBottomScrollContext } from '@/shared/ui/bottom-scroll-area';

export function StreamErrorCallout() {
  const queryClient = useQueryClient();
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { scrollToBottom } = useBottomScrollContext();
  const { streamMutate } = useChatStreamMutation();
  const { variables } = useChatStreamMutationState({
    chatId: Number(chatId),
  });

  const handleRetry = async () => {
    if (!variables || !variables.payload) return;

    await queryClient.invalidateQueries(chatsQueries.getChatsByChatIdMessages({ chatId: Number(chatId) }));

    streamMutate(Number(chatId), variables.payload, {
      message_send: () => {
        scrollToBottom({});
      },
    });
  };

  return (
    <ChatAlert
      message="응답을 받는 도중 연결이 끊어졌습니다."
      type="error"
      button={{
        label: '다시 시도',
        onClick: handleRetry,
      }}
    />
  );
}
