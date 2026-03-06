/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ProblemExplanation } from '@/entities/problems/ui/problem-explanation';
import { MultipleChoiceItem } from '@/entities/problems/ui/problem-multiple-choice-item';
import type { ChatProblemDetailResponseDto, MultipleChoiceProblemResponseDto } from '@/shared/api/__generated__/dto';
import { cn } from '@/shared/utils/utils';

type MultipleChoiceProblemProps = {
  lastAnswer: ChatProblemDetailResponseDto['last_answer'];
  status: ChatProblemDetailResponseDto['status'];
  explanation: MultipleChoiceProblemResponseDto['content']['explanation'];
  choices: MultipleChoiceProblemResponseDto['content']['choices'];
  isReadOnly?: boolean;
  chatId: number;
  problemId: string;
  value?: number[];
  onChange?: (value: number[]) => void;
};

export function ProblemMultipleChoiceOptions({
  lastAnswer,
  status,
  explanation,
  choices,
  isReadOnly = false,
  chatId,
  problemId,
  value = [],
  onChange,
}: MultipleChoiceProblemProps) {
  const lastAnswers = parseLastAnswers(lastAnswer);

  const handleCheckedChange = (optionNo: number, checked: boolean) => {
    if (checked) {
      onChange?.([...value, optionNo]);
    } else {
      onChange?.(value.filter((v) => v !== optionNo));
    }
  };

  const showExplanation = status === '정답' || status === '복습 완료';

  return (
    <div className="flex flex-col gap-y-[1em]">
      <div className={cn('flex flex-col gap-y-[0.5em]', isReadOnly && 'pointer-events-none')}>
        {choices?.map((option) => (
          <MultipleChoiceItem
            key={option.no}
            option={option}
            status={status}
            lastAnswers={lastAnswers}
            selectedValues={value}
            chatId={chatId}
            problemId={problemId}
            onCheckedChange={(checked) => handleCheckedChange(option.no, Boolean(checked))}
            explanationComponent={() => null}
          />
        ))}
      </div>

      {showExplanation && <ProblemExplanation explanation={explanation} status={status} />}
    </div>
  );
}

function parseLastAnswers(lastAnswer: ChatProblemDetailResponseDto['last_answer']): number[] {
  if (!lastAnswer) return [];

  try {
    const parsed = JSON.parse(lastAnswer);
    if (Array.isArray(parsed)) {
      return parsed.map(Number).filter((n) => !Number.isNaN(n));
    }
  } catch {
    // lastAnswer가 단일 숫자 문자열인 경우
    const num = Number(lastAnswer);
    if (!Number.isNaN(num)) {
      return [num];
    }
  }

  return [];
}
