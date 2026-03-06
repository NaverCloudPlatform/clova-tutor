/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { CircleIcon, MinusIcon, TriangleIcon, XIcon } from 'lucide-react';
import { match } from 'ts-pattern';
import type { ProblemStatusDto } from '@/shared/api/__generated__/dto';
import { Badge } from '@/shared/ui/badge';
import { cn } from '@/shared/utils/utils';

type Props = {
  status: ProblemStatusDto;
  className?: string;
};

export function ProblemStatusBadge({ status, className }: Props) {
  const badgeInfo = match(status)
    .with('풀지 않음', () => ({
      label: '풀지 않음',
      color: 'bg-cool-gray-300 dark:bg-cool-gray-1500',
      icon: <MinusIcon className="stroke-muted-foreground size-auto" />,
    }))
    .with('정답', () => ({
      label: '정답',
      color: 'bg-neon-blue-100 text-neon-blue-700',
      icon: <CircleIcon className="stroke-primary size-auto" />,
    }))
    .with('오답', () => ({
      label: '복습 필요',
      color: 'bg-accent-red-100 text-accent-red-700',
      icon: <XIcon className="stroke-accent-red-700 size-auto" />,
    }))
    .with('복습 완료', () => ({
      label: '복습 완료',
      color: 'bg-accent-green-100 text-accent-green-700',
      icon: <TriangleIcon className="stroke-accent-green-700 size-auto" />,
    }))
    .exhaustive();

  return (
    <Badge
      aria-label={badgeInfo.label}
      className={cn('shrink-0 text-foreground font-semibold rounded-sm p-0.5', badgeInfo.color, className)}
    >
      {badgeInfo.icon}
    </Badge>
  );
}
