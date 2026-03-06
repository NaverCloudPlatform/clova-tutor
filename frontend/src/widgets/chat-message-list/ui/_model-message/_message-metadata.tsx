/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { compact } from 'es-toolkit';
import { isChatRecommandedVisible } from '@/entities/chats/rules/tool';
import { ModelMessageAskFollowupQuestion } from '@/features/message-actions/ui/model-message-ask-followup-question';
import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import type { ChatMessageProps } from '../../types/chats';

type MessageMetadataProps = {
  message: ChatMessageResponseDto;
} & Pick<ChatMessageProps, 'isLastMessage'>;

export function MessageMetadata({ message, isLastMessage }: MessageMetadataProps) {
  const MetadataComponents = compact([
    isLastMessage && message.metadata.tools && isChatRecommandedVisible(message) && (
      <ModelMessageAskFollowupQuestion key="chat-recommanded" tools={message.metadata.tools} />
    ),
  ]);

  if (MetadataComponents.length === 0) return null;

  return <div className="last:pb-6">{MetadataComponents}</div>;
}
