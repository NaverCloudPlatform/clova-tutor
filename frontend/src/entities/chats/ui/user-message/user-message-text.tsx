/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ChatMarkdown } from '@/entities/chats/ui/chat-markdown';
import type { TextContentDto } from '@/shared/api/__generated__/dto';

type Props = {
  content: TextContentDto;
};

export function UserMessageText({ content }: Props) {
  return <ChatMarkdown>{content.value.text}</ChatMarkdown>;
}
