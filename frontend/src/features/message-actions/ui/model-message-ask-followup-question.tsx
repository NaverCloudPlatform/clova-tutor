/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import type { GRAMMER_QUESTION } from '@/entities/chats/constants/grammer-question';
import type { WORD_QUESTION } from '@/entities/chats/constants/word-question';
import { useChatStreamMutation } from '@/entities/chats/hooks/use-chat-stream';
import { ModelMessageRecommendations } from '@/entities/chats/ui/model-message/model-message-recommendations';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import type { ToolInfoDto } from '@/shared/api/__generated__/dto';
import { useBottomScrollContext } from '@/shared/ui/bottom-scroll-area';

type Props = {
  tools: ToolInfoDto[];
};

export function ModelMessageAskFollowupQuestion({ tools }: Props) {
  const { chat_id: chatId } = useParams({
    strict: false,
  });
  const { scrollToBottom } = useBottomScrollContext();
  const insertText = useRichEditorStore((state) => state.insertText);
  const { streamMutate } = useChatStreamMutation();

  const handleClick = (question: (typeof WORD_QUESTION)[number] | (typeof GRAMMER_QUESTION)[number]) => {
    insertText(question.question);

    streamMutate(
      Number(chatId),
      {
        contents: [
          {
            m_type: 'text',
            value: { text: question.question },
          } as const,
        ],
        metadata: {
          system_hints: undefined,
        },
      },
      {
        message_send: () => {
          // 메시지 전송 후 유저의 메시지가 추가되기 전에 스크롤이 이루어지는 것을 방지하기 위해 100ms 대기 후 스크롤 이벤트 실행
          setTimeout(() => {
            scrollToBottom({});
          }, 100);
        },
      },
    );
  };

  return <ModelMessageRecommendations tools={tools} onQuestionClick={handleClick} />;
}
