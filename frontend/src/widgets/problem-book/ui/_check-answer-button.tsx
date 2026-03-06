/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { useFormContext } from 'react-hook-form';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { Button } from '@/shared/ui/button';
import type { ProblemBookProps } from '../types/props';

type CheckAnswerButtonProps = ProblemBookProps;

export function CheckAnswerButton({ problemId, chatId }: CheckAnswerButtonProps) {
  const { formState } = useFormContext();
  const { data: problemStatus } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      problemId: problemId,
      chatId: chatId,
    }),
    select: (data) => data.status,
  });

  return (
    <Button
      type="submit"
      size="lg"
      className="font-bold px-12"
      disabled={!formState.isValid || problemStatus === '정답' || problemStatus === '복습 완료'}
    >
      채점하기
    </Button>
  );
}
