/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { useChatStreamMutation } from '@/entities/chats/hooks/use-chat-stream';
import type { SystemHintDto } from '@/shared/api/__generated__/dto';
import { useBottomScrollContext } from '@/shared/ui/bottom-scroll-area';
import { Button } from '@/shared/ui/button';
import { Tooltip, TooltipTrigger } from '@/shared/ui/tooltip';

type SystemHintButtonProps = {
  buttonLabel: string;
  buttonIcon: React.ReactNode;
  systemHint: SystemHintDto;
};

export function SystemHintButton({ buttonLabel, buttonIcon, systemHint }: SystemHintButtonProps) {
  const { chat_id: chatId } = useParams({
    strict: false,
  });
  const { scrollToBottom } = useBottomScrollContext();
  const { streamMutate } = useChatStreamMutation();

  const handleSubmitQuiz = () => {
    streamMutate(
      Number(chatId),
      {
        contents: [],
        metadata: {
          system_hints: [systemHint],
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

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="text-xs text-muted-foreground rounded-full px-3 py-1.5 font-base shadow-none"
          aria-label={buttonLabel}
          onClick={handleSubmitQuiz}
        >
          {buttonIcon}
          {buttonLabel}
        </Button>
      </TooltipTrigger>
    </Tooltip>
  );
}
