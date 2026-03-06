/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { SquareChartGanttIcon } from 'lucide-react';
import { isTranslationVisible } from '@/entities/chats/rules/tool';
import { SystemHintButton } from '@/features/message-actions/ui/model-message-system-hint-button';
import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import type { ChatMessageProps } from '../../types/chats';
import { ChatMenuList } from '../_chat-menu/chat-menu-list';

type MessageMenuListProps = {
  message: ChatMessageResponseDto;
} & Pick<ChatMessageProps, 'isLastMessage'>;

export function MessageMenuList({ message, isLastMessage }: MessageMenuListProps) {
  return (
    <div className="flex items-center space-x-1">
      {isLastMessage && isTranslationVisible(message) && <TranslationButton />}

      <ChatMenuList message={message} />
    </div>
  );
}

function TranslationButton() {
  return (
    <SystemHintButton
      buttonLabel="문장 직독직해 하기"
      buttonIcon={<SquareChartGanttIcon className="stroke-primary" />}
      systemHint="translation_button"
    />
  );
}
