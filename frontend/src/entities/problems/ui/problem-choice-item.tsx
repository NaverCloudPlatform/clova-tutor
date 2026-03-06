/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { cva } from 'class-variance-authority';
import { CheckIcon } from 'lucide-react';
import { match, P } from 'ts-pattern';
import { MarkdownBase } from '@/packages/markdown/ui/markdown-base';
import type { ChatProblemDetailResponseDto, ProblemChoiceDto } from '@/shared/api/__generated__/dto';
import { Label } from '@/shared/ui/label';
import { RadioGroupItem } from '@/shared/ui/radio-group';
import { cn } from '@/shared/utils/utils';

const choiceLabelVariants = cva('flex flex-col gap-0 items-start cursor-pointer w-full px-[0.5em] rounded-md', {
  variants: {
    problemStatus: {
      정답: 'opacity-50',
      '복습 완료': 'opacity-50',
      오답: '',
      '풀지 않음': '',
    },
    choiceItemStatus: {
      correctChoice: '',
      wrongChoice: '',
      neutralChoice: '',
    },
    isSelected: {
      true: 'font-bold bg-slate-100 dark:bg-slate-800',
      false: '',
    },
  },
  compoundVariants: [
    {
      problemStatus: '정답',
      choiceItemStatus: 'correctChoice',
      class: 'opacity-100 text-primary stroke-primary font-bold bg-neon-blue-100 dark:bg-neon-blue-1000',
    },
    {
      problemStatus: '복습 완료',
      choiceItemStatus: 'correctChoice',
      class:
        'opacity-100 bg-accent-green-100 dark:bg-accent-green-1000 text-accent-green-800 dark:text-accent-green-300 stroke-accent-green-800 dark:stroke-accent-green-300 font-bold',
    },
    {
      problemStatus: '오답',
      choiceItemStatus: 'wrongChoice',
      class: 'text-destructive stroke-destructive font-bold bg-accent-red-100 dark:bg-accent-red-1000',
    },
  ],
  defaultVariants: {
    problemStatus: '풀지 않음',
    choiceItemStatus: 'neutralChoice',
    isSelected: false,
  },
});

const choiceBadgeVariants = cva(
  'flex items-center justify-center rounded-full size-[1.25em] text-[0.75em] border border-accent-foreground',
  {
    variants: {
      problemStatus: {
        정답: '',
        '복습 완료': '',
        오답: '',
        '풀지 않음': '',
      },
      choiceItemStatus: {
        correctChoice: '',
        wrongChoice: '',
        neutralChoice: '',
      },
      isSelected: {
        true: 'font-bold',
        false: '',
      },
    },
    compoundVariants: [
      {
        problemStatus: '정답',
        choiceItemStatus: 'correctChoice',
        class: 'text-primary border-primary',
      },
      {
        problemStatus: '복습 완료',
        choiceItemStatus: 'correctChoice',
        class: 'text-accent-green-800 border-accent-green-800',
      },
      {
        problemStatus: '오답',
        choiceItemStatus: 'wrongChoice',
        class: 'text-destructive border-destructive',
      },
    ],
    defaultVariants: {
      problemStatus: '풀지 않음',
      choiceItemStatus: 'neutralChoice',
      isSelected: false,
    },
  },
);

type ChoiceItemProps = {
  option: ProblemChoiceDto;
  status: ChatProblemDetailResponseDto['status'];
  lastAnswer: ChatProblemDetailResponseDto['last_answer'];
  selectedValue: number | null;
  chatId: number;
  problemId: string;
  explanationComponent: (choiceItemStatus: 'correctChoice' | 'wrongChoice' | 'neutralChoice') => React.ReactNode;
};

export function ChoiceItem({
  option,
  status,
  lastAnswer,
  selectedValue,
  chatId,
  problemId,
  explanationComponent,
}: ChoiceItemProps) {
  const isSelected = selectedValue === option.no;
  const choiceItemStatus =
    option.no !== Number(lastAnswer)
      ? ('neutralChoice' as const)
      : match(status)
          .with(P.union('정답', '복습 완료'), () => 'correctChoice' as const)
          .with('오답', () => 'wrongChoice' as const)
          .otherwise(() => 'neutralChoice' as const);

  const uniqueId = `option-${chatId}-${problemId}-${option.no}`;

  return (
    <div className="flex flex-col gap-y-[0.5em] cursor-pointer">
      <RadioGroupItem value={option.no.toString()} id={uniqueId} className="sr-only" />

      <Label
        htmlFor={uniqueId}
        className={cn(choiceLabelVariants({ problemStatus: status, choiceItemStatus, isSelected }))}
      >
        <div className="flex items-center gap-x-[0.5em] relative">
          {isSelected && ['오답', '풀지 않음'].includes(status) && (
            <CheckIcon className="absolute -top-[0.125em] -left-[0.25em] size-[2em]" />
          )}
          <div className={cn(choiceBadgeVariants({ problemStatus: status, choiceItemStatus, isSelected }))}>
            {option.no}
          </div>
          <MarkdownBase>{option.inst}</MarkdownBase>
        </div>

        {explanationComponent(choiceItemStatus)}
      </Label>
    </div>
  );
}
