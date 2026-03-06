/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import { CopyButton } from '@/shared/ui/common/copy-button';

type ChatCopyButtonProps = {
  message: ChatMessageResponseDto;
};

export function ChatCopyButton({ message }: ChatCopyButtonProps) {
  const copyContent = message.contents
    .filter((content) => content.m_type === 'text')
    .map((content) => content.value.text)
    .join('');

  return <CopyButton copyContent={copyContent} />;
}
