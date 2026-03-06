/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { isMatching, P } from 'ts-pattern';
import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import { BAN } from '../constants/text';

export const isChatRecommandedVisible = (message: unknown) => {
  return isMatching({
    contents: P.array(
      P.union({ m_type: P.not('text') }, { m_type: 'text', value: { text: P.not(P.string.includes(BAN)) } }),
    ),
    metadata: {
      tools: P.when(
        (tools) =>
          Array.isArray(tools) && tools.some((tool) => tool.name === 'eng_voca' || tool.name === 'eng_grammar'),
      ),
    },
  })(message);
};

export const isUserChatVisible = (message: ChatMessageResponseDto) => {
  return !isMatching({
    metadata: {
      system_hints: P.array(P.union('translation_button')),
    },
  })(message);
};

export const isTranslationVisible = (message: ChatMessageResponseDto) => {
  return isMatching({
    contents: P.array(
      P.union({ m_type: P.not('text') }, { m_type: 'text', value: { text: P.not(P.string.includes(BAN)) } }),
    ),
    metadata: {
      tools: P.when(
        (tools) =>
          Array.isArray(tools) &&
          tools.some(
            (tool) => tool.name === 'eng_plain_translation' && tool.value?.translation_button_visible === true,
          ),
      ),
    },
  })(message);
};
