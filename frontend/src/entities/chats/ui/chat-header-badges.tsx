/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { compact } from 'es-toolkit';
import { GoalIcon } from 'lucide-react';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';
import { cn } from '@/shared/utils/utils';

type ChatHeaderBadgesProps = {
  chat: ChatResponseDto;
} & React.ComponentProps<'div'>;

export function ChatHeaderBadges({ chat, className, ...props }: ChatHeaderBadgesProps) {
  const Badges = compact([
    chat.has_active_goal && (
      <p key="active-goal" className="flex items-center gap-x-1 text-primary font-semibold text-xs">
        <GoalIcon className="stroke-primary size-3" />
        목표 진행중
      </p>
    ),
  ]);

  if (Badges.length === 0) return null;

  return (
    <div className={cn('flex items-center gap-x-1', className)} {...props}>
      {Badges}
    </div>
  );
}
