/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { useGetChatsByChatIdMessagesSuspenseQuery } from '@/entities/chats/api/queries';
import { isUserChatVisible } from '@/entities/chats/rules/tool';
import { UserChatBadge } from '@/entities/chats/ui/user-message/user-message-badge';
import { UserMessaegContent } from '@/entities/chats/ui/user-message/user-message-content';
import { log } from '@/shared/core/log';
import type { ChatMessageProps } from '../../types/chats';
import { ProblemLinkBadge } from './_problem-link';

type MessageContentProps = Pick<ChatMessageProps, 'messageIndex'>;

export function MessageContent({ messageIndex }: MessageContentProps) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: message } = useGetChatsByChatIdMessagesSuspenseQuery(
    {
      chatId: Number(chatId),
    },
    {
      select: (data) => {
        return data.data[messageIndex].type === 'chat' ? data.data[messageIndex] : null;
      },
    },
  );

  if (!message) {
    log.error('컴포넌트 선언 에러');
    return null;
  }

  if (!isUserChatVisible(message)) {
    return null;
  }

  return (
    <UserMessaegContent
      message={message}
      userChatBadge={<UserChatBadge message={message} ProblemLinkBadgeComponent={ProblemLinkBadge} />}
    />
  );
}
