/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { LinkIcon } from 'lucide-react';

import { Skeleton } from '@/shared/ui/skeleton';
import { cn } from '@/shared/utils/utils';

type UserMessageProblemLinkBadgeLabelProps = {
  problemNumber: number;
} & React.ComponentProps<'div'>;

export function UserMessageProblemLinkBadgeLabel({ problemNumber, ...props }: UserMessageProblemLinkBadgeLabelProps) {
  const { className, ...rest } = props;

  return (
    <div className={cn('flex items-center gap-1.5', className)} {...rest}>
      <LinkIcon className="size-2.5 text-primary" />
      <span className="text-xs text-primary ai-text">{problemNumber}번 문제 질문</span>
    </div>
  );
}

export function ProblemLinkBadgeLabelSkeleton() {
  return (
    <div className="">
      <LinkIcon className="w-4 h-4 text-blue-700" />
      <Skeleton className="w-full h-4" />
    </div>
  );
}
