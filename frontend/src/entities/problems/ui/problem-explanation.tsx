/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ProblemStatusBadge } from '@/entities/problems/ui/problem-status-badge';
import type { ChatProblemDetailResponseDto } from '@/shared/api/__generated__/dto';
import { Item, ItemContent, ItemDescription, ItemTitle } from '@/shared/ui/item';
import { cn } from '@/shared/utils/utils';

export type ProblemExplanationProps = {
  explanation: ChatProblemDetailResponseDto['problem_info']['content']['explanation'];
  status: ChatProblemDetailResponseDto['status'];
};

export function ProblemExplanation({ explanation, status }: ProblemExplanationProps) {
  return (
    <Item
      size="sm"
      className={cn({
        'text-primary bg-neon-blue-100 dark:bg-neon-blue-1000': status === '정답',
        'text-accent-green-800 dark:text-accent-green-300 bg-accent-green-100 dark:bg-accent-green-1000':
          status === '복습 완료',
      })}
    >
      <ItemContent>
        <ItemTitle className="font-semibold">
          <ProblemStatusBadge className="p-0 rounded-none" status={status} />
          정답입니다!
        </ItemTitle>
        <ItemDescription className="text-foreground">{explanation}</ItemDescription>
      </ItemContent>
    </Item>
  );
}
