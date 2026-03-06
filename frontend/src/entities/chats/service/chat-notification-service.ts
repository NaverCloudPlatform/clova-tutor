/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import type { Subject } from '@/shared/types/common';
import { chatNotificationToast } from '../ui/chat-notification';

export class ChatNotificationService {
  private readonly chatId: number;
  private readonly subject: Subject;

  constructor(chatId: number, subject: Subject) {
    this.chatId = chatId;
    this.subject = subject;
  }

  static getCurrentPageChatId() {
    const pathSegments = window.location.pathname.split('/');
    const chatsIndex = pathSegments.findIndex((segment) => segment === 'chats');
    return chatsIndex !== -1 && chatsIndex + 1 < pathSegments.length ? Number(pathSegments[chatsIndex + 1]) : null;
  }

  showNotification(message: ChatMessageResponseDto) {
    const { chatId, subject } = this;
    const currentPageChatId = ChatNotificationService.getCurrentPageChatId();

    if (!message || currentPageChatId === chatId) return;

    chatNotificationToast({
      chatId,
      message,
      subject,
    });
  }
}
