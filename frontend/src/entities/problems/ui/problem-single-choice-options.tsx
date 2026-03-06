/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ChoiceItem } from '@/entities/problems/ui/problem-choice-item';
import { ProblemExplanation } from '@/entities/problems/ui/problem-explanation';
import type { ChatProblemDetailResponseDto, SingleChoiceProblemResponseDto } from '@/shared/api/__generated__/dto';
import { RadioGroup } from '@/shared/ui/radio-group';
import { cn } from '@/shared/utils/utils';

type SingleChoiceProblemProps = {
  lastAnswer: ChatProblemDetailResponseDto['last_answer'];
  status: ChatProblemDetailResponseDto['status'];
  explanation: SingleChoiceProblemResponseDto['content']['explanation'];
  choices: SingleChoiceProblemResponseDto['content']['choices'];
  isReadOnly?: boolean;
  chatId: number;
  problemId: string;
  value?: number | null;
  onChange?: (value: number) => void;
};

export function ProblemSingleChoiceOptions({
  lastAnswer,
  status,
  explanation,
  choices,
  isReadOnly = false,
  chatId,
  problemId,
  value,
  onChange,
}: SingleChoiceProblemProps) {
  return (
    <div className="flex flex-col gap-y-[1em]">
      <RadioGroup
        className={cn('flex flex-col gap-y-[0.5em]', isReadOnly && 'pointer-events-none')}
        disabled={isReadOnly}
        value={value?.toString()}
        onValueChange={(v) => onChange?.(Number(v))}
      >
        {choices?.map((option) => {
          return (
            <ChoiceItem
              key={option.no}
              option={option}
              status={status}
              lastAnswer={lastAnswer}
              selectedValue={value ?? null}
              chatId={chatId}
              problemId={problemId}
              explanationComponent={(choiceItemStatus) =>
                choiceItemStatus === 'correctChoice' && (
                  <div className="pb-[0.25em]">
                    <ProblemExplanation explanation={explanation} status={status} />
                  </div>
                )
              }
            />
          );
        })}
      </RadioGroup>
    </div>
  );
}
