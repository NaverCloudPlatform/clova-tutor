/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ChatMarkdown } from '@/entities/chats/ui/chat-markdown';
import type { TextContentDto } from '@/shared/api/__generated__/dto';

type Props = {
  content: TextContentDto;
  messageId?: number;
};

export function ModelTextMessage({ content, messageId }: Props) {
  return (
    <div className="my-2">
      <ChatMarkdown calloutPrefix={messageId != null ? `msg-${messageId}` : undefined}>
        {content.value.text}
      </ChatMarkdown>
    </div>
  );
}
