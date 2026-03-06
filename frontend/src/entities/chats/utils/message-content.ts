/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';

export function sortMessageContents(contents: ChatMessageResponseDto['contents']) {
  return contents.toSorted((a, b) => {
    const priority = {
      images: 1,
      text: 2,
      problem_recommended: 3,
      problem_link: 0,
      quote: 0,
    };
    return priority[a.m_type] - priority[b.m_type];
  });
}
