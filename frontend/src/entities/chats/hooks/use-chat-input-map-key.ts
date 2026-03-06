/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { useSubject } from './use-subject';

export function useChatInputMapKey() {
  const { subject } = useSubject();
  const { chat_id: chatId } = useParams({
    strict: false,
  });

  return chatId ? Number(chatId) : subject;
}
