/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { RefreshCcwIcon } from 'lucide-react';
import type { PropsWithChildren } from 'react';
import { useChatStreamMutation } from '@/entities/chats/hooks/use-chat-stream';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { useBottomScrollContext } from '@/shared/ui/bottom-scroll-area';
import { Button } from '@/shared/ui/button';

export function UserMessageRetryWrapper({ children }: PropsWithChildren) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { scrollToBottom } = useBottomScrollContext();
  const { retryStreamMutate } = useChatStreamMutation();
  const { variables } = useChatStreamMutationState({
    chatId: Number(chatId),
  });

  const handleRetry = () => {
    if (!variables || !variables.payload) return;

    retryStreamMutate(Number(chatId), variables.payload, {
      message_send: () => {
        scrollToBottom({});
      },
    });
  };

  return (
    <div className="flex items-center flex-col gap-2 self-end">
      <div className="flex gap-1 items-end self-end">
        <Button variant="ghost" size="icon" className="text-muted-foreground" onClick={handleRetry}>
          <RefreshCcwIcon className="size-3" />
        </Button>
        {children}
      </div>

      <p className="text-sm text-muted-foreground">문제가 발생했습니다. 다시 시도해주세요.</p>
    </div>
  );
}
