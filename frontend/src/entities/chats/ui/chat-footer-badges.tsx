/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { compact } from 'es-toolkit';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';
import { Badge } from '@/shared/ui/badge';
import { cn } from '@/shared/utils/utils';
import { useChatStore } from '../store/chats';

type ChatFooterBadgesProps = {
  chat: ChatResponseDto;
} & React.ComponentProps<'div'>;

export function ChatFooterBadges({ chat, className, ...props }: ChatFooterBadgesProps) {
  const hasChatInput = useChatStore((state) => state.hasChatInput);

  const Badges = compact([
    hasChatInput(chat.id) && (
      <Badge key="writing" variant="secondary">
        작성중
      </Badge>
    ),
    chat.has_problem && (
      <Badge key="problem" variant="secondary" className="bg-accent-blue-100/70">
        학습 문제 추천
      </Badge>
    ),
  ]);

  if (Badges.length === 0) return null;

  return (
    <div className={cn('flex items-center gap-x-1', className)} {...props}>
      {Badges}
    </div>
  );
}
