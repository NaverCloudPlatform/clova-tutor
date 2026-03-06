/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { compact, keyBy } from 'es-toolkit';
import React from 'react';
import type { ChatMessageResponseDto, ProblemLinkContentDto } from '@/shared/api/__generated__/dto';

type UserChatBadgeProps = {
  message: ChatMessageResponseDto;
  ProblemLinkBadgeComponent: React.ComponentType<{ content: ProblemLinkContentDto }>;
};

export function UserChatBadge({ message, ProblemLinkBadgeComponent }: UserChatBadgeProps) {
  const contentByMType = keyBy(message.contents, (content) => content.m_type);

  const BadgeComponents = compact([
    contentByMType.problem_link?.m_type === 'problem_link' && (
      <ProblemLinkBadgeComponent content={contentByMType.problem_link} />
    ),
  ]);

  if (BadgeComponents.length === 0) return null;

  return (
    <section role="note">
      {BadgeComponents.map((badge) => (
        <React.Fragment key={badge.key}>{badge}</React.Fragment>
      ))}
    </section>
  );
}
