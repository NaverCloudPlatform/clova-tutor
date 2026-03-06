/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { useParams } from '@tanstack/react-router';
import { useEffect, useRef } from 'react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { useChatStreamResumeMutation } from '@/entities/chats/hooks/use-chat-stream-resume';
import { withSuspense } from '@/shared/hoc/with-suspense';
import { useBottomScrollContext } from '@/shared/ui/bottom-scroll-area';

export const StreamStatusChecker = withSuspense(() => {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: streamStatus } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdStreamStatus({
      chatId: Number(chatId),
    }),
  });
  const { isStreaming, context } = useChatStreamMutationState({
    chatId: Number(chatId),
  });
  const hasResumedRef = useRef(false);

  if (!isStreaming && streamStatus?.status === 'IS_STREAMING' && !context?.isCreateChat) {
    return <StreamResume chatId={Number(chatId)} hasResumedRef={hasResumedRef} />;
  }

  return null;
});

type StreamResumeProps = {
  chatId: number;
  hasResumedRef: React.RefObject<boolean>;
};

function StreamResume({ chatId, hasResumedRef }: StreamResumeProps) {
  const { scrollToBottom } = useBottomScrollContext();
  const { streamResumeMutate } = useChatStreamResumeMutation();

  // biome-ignore lint/correctness/useExhaustiveDependencies: 스트리밍 진행중일 때 마운트되는 컴포넌트로 최초 1회만 복구 로직 실행
  useEffect(() => {
    if (hasResumedRef.current) return;

    hasResumedRef.current = true;

    streamResumeMutate(Number(chatId), {
      message_start: () => {
        scrollToBottom({ smooth: false });
      },
    });
  }, []);

  return null;
}
