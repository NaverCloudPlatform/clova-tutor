/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import { ChatCopyButton } from './chat-copy-button';

type Props = {
  message: ChatMessageResponseDto;
};

export function ChatMenuList({ message }: Props) {
  return (
    <div className="flex">
      <ChatCopyButton message={message} />
    </div>
  );
}
