/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { debounce } from 'es-toolkit';
import { useChatStreamMutation } from '@/entities/chats/hooks/use-chat-stream';
import type { ChatMessageCreateRequestBodyDto } from '@/shared/api/__generated__/dto';
import { useBottomScrollContext } from '@/shared/ui/bottom-scroll-area';
import { TutorChatInputForm } from './tutor-chat-input-form';

export function TutorChatInput() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { scrollToBottom } = useBottomScrollContext();
  const { streamMutate } = useChatStreamMutation();

  const handleSubmit = debounce((payload: ChatMessageCreateRequestBodyDto) => {
    streamMutate(Number(chatId), payload, {
      message_send: () => {
        // 메시지 전송 후 유저의 메시지가 추가되기 전에 스크롤이 이루어지는 것을 방지하기 위해 100ms 대기 후 스크롤 이벤트 실행
        setTimeout(() => {
          scrollToBottom({});
        }, 100);
      },
    });
  }, 200);

  return <TutorChatInputForm onSubmit={handleSubmit} />;
}
