/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { GraduationCapIcon } from 'lucide-react';
import type { ProblemRecommendedValueDto } from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import { cn } from '@/shared/utils/utils';

type ModelProblemRecommendedMessageViewProps = {
  content: ProblemRecommendedValueDto;
  buttonProps?: React.ComponentProps<typeof Button>;
};

export function ModelProblemRecommendedMessageView({ content, buttonProps }: ModelProblemRecommendedMessageViewProps) {
  return (
    <div className="flex gap-x-2 justify-between bg-muted border px-6 py-5 rounded-lg animate-in fade-in-0 duration-500 mb-2">
      <div className="flex gap-x-2.5">
        <GraduationCapIcon className="size-6 stroke-primary" />

        <div>
          <p className="font-semibold">학습 문제 추천</p>
          <p className="text-sm text-muted-foreground">{content.category}</p>
        </div>
      </div>

      <Button size="lg" {...buttonProps} className={cn('rounded-full', buttonProps?.className)}>
        열기
      </Button>
    </div>
  );
}
