/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient } from '@tanstack/react-query';
import { useParams } from '@tanstack/react-router';
import { useEffect } from 'react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { ASSISTANT_STREAMING_MESSAGE_ID } from '@/entities/chats/constants/streaming';
import { ModelProblemRecommendedMessageView } from '@/entities/chats/ui/model-message/model-message-problem-recommended';
import { useStudyArea } from '@/pages/_student/$subject/chats/$chat_id/problem/-hooks/use-study-area';
import type { ChatMessageResponseDto, ProblemRecommendedValueDto } from '@/shared/api/__generated__/dto';
import { cn } from '@/shared/utils/utils';

type MessageProblemRecommendedProps = {
  messageId?: ChatMessageResponseDto['id'];
  content: ProblemRecommendedValueDto;
  isLastMessage?: boolean;
};

export function MessageProblemRecommended({ messageId, content, isLastMessage }: MessageProblemRecommendedProps) {
  const { problem_id } = content;
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const queryClient = useQueryClient();
  const { isStudyAreaOpen, goToProblem } = useStudyArea();

  // biome-ignore lint/correctness/useExhaustiveDependencies: 모델 응답 트리거시 학습컨텐츠 영역 오픈
  useEffect(() => {
    if (!problem_id || !isLastMessage) return;
    if (messageId !== ASSISTANT_STREAMING_MESSAGE_ID) return;

    goToProblem(problem_id);

    //NOTE: 추천받은 문제를 목록에서 보기 위해 문제 리스트 캐시 무효화
    queryClient.invalidateQueries({
      queryKey: chatsQueries.getChatsByChatIdProblems({ chatId: Number(chatId) }).queryKey,
    });
  }, [problem_id]);

  const handleClick = () => {
    goToProblem(content.problem_id);
  };

  return (
    <ModelProblemRecommendedMessageView
      content={content}
      buttonProps={{
        className: cn(isStudyAreaOpen ? 'hidden' : 'block', 'rounded-full'),
        onClick: handleClick,
      }}
    />
  );
}
