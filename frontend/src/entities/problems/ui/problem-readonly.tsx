/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { match } from 'ts-pattern';
import type { ProblemResponseDto, ProblemStatusDto } from '@/shared/api/__generated__/dto';
import { Skeleton } from '@/shared/ui/skeleton';
import { cn } from '@/shared/utils/utils';
import { ProblemMetadataBadge } from './problem-metadata-badge';
import { ProblemMultipleChoiceOptions } from './problem-multiple-choice-options';
import { ProblemQuestion } from './problem-question';
import { ProblemSingleChoiceOptions } from './problem-single-choice-options';

type Props = {
  problem: ProblemResponseDto;
  status?: ProblemStatusDto;
  className?: string;
  hideMetadata?: boolean;
};

export function ProblemReadOnly({ problem, status = '풀지 않음', className, hideMetadata = false }: Props) {
  return (
    <div className={cn('h-full pointer-events-none', className)}>
      <div className="flex flex-col">
        {!hideMetadata && (
          <ProblemMetadataBadge
            grade={problem.content.grade}
            level={problem.content.level}
            category={problem.content.category}
          />
        )}
        <ProblemQuestion problem={problem.content.problem} />
      </div>

      {match(problem)
        .with({ type: '단일선택 객관식' }, (singleChoiceProblem) => (
          <div className="space-y-1 select-none">
            <ProblemSingleChoiceOptions
              chatId={-1}
              problemId={problem.id}
              lastAnswer={null}
              status={status}
              explanation={problem.content.explanation}
              choices={singleChoiceProblem.content.choices}
              isReadOnly
            />
          </div>
        ))
        .with({ type: '다중선택 객관식' }, (multipleChoiceProblem) => (
          <div className="space-y-1 select-none">
            <ProblemMultipleChoiceOptions
              chatId={-1}
              problemId={problem.id}
              lastAnswer={null}
              status={status}
              explanation={problem.content.explanation}
              choices={multipleChoiceProblem.content.choices}
              isReadOnly
            />
          </div>
        ))
        .with({ type: '단일응답 주관식' }, () => null)
        .otherwise(() => null)}
    </div>
  );
}

export function ProblemBookSkeleton() {
  return (
    <div className="px-1 flex-1">
      <div className="flex flex-col gap-y-4">
        <div className="flex flex-col gap-y-2">
          <Skeleton className="h-7 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
        <div className="flex flex-col gap-y-2">
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
        </div>
      </div>
    </div>
  );
}
