/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { StarIcon } from 'lucide-react';
import { gradeToName } from '@/entities/users/utils/user-grade';
import type { ChoiceProblemContentDto } from '@/shared/api/__generated__/dto';
import { Skeleton } from '@/shared/ui/skeleton';
import { cn } from '@/shared/utils/utils';
import { getDifficultyLevelText } from '../utils/difficulty';

type ProblemMetadataBadgeProps = Pick<ChoiceProblemContentDto, 'grade' | 'level' | 'category'> & {
  classNames?: {
    base?: string;
    starWrapper?: string;
    star?: string;
    text?: string;
  };
};

export function ProblemMetadataBadge({ grade, level, category, classNames }: ProblemMetadataBadgeProps) {
  const gradeText = gradeToName(grade, { short: true });
  const difficultyLevel = getDifficultyLevelText(level);

  return (
    <div className={cn('flex items-center gap-x-[0.5em]', classNames?.base)}>
      <div className={cn('flex items-center', classNames?.starWrapper)}>
        {new Array(3).fill(0).map((_, index) => {
          const isFilled = difficultyLevel !== null && index < difficultyLevel;

          return (
            <StarIcon
              key={`star-${
                // biome-ignore lint/suspicious/noArrayIndexKey: 순서 바뀌지 않음
                index
              }`}
              className={cn(
                isFilled ? 'size-[0.75em] fill-chart-4 stroke-chart-4' : 'size-[0.75em] stroke-chart-4',
                classNames?.star,
              )}
            />
          );
        })}
      </div>
      <p className={cn('text-[0.75em] text-muted-foreground', classNames?.text)}>
        [{gradeText}] {category}
      </p>
    </div>
  );
}

export function ProblemMetadataBadgeSkeleton({ classNames }: Pick<ProblemMetadataBadgeProps, 'classNames'>) {
  return (
    <div className={cn('flex items-center gap-x-[0.5em]', classNames?.base)}>
      <div className={cn('flex items-center', classNames?.starWrapper)}>
        {new Array(3).fill(0).map((_, index) => {
          return (
            <StarIcon
              key={`star-${
                // biome-ignore lint/suspicious/noArrayIndexKey: 순서 바뀌지 않음
                index
              }`}
              className={cn('size-[0.75em] stroke-chart-4', classNames?.star)}
            />
          );
        })}
      </div>
      <Skeleton className={cn(classNames?.text)} />
    </div>
  );
}
