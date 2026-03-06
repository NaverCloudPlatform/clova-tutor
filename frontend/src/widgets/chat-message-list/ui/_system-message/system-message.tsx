/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { match } from 'ts-pattern';
import { useGetChatsByChatIdMessagesSuspenseQuery } from '@/entities/chats/api/queries';
import { SystemMessaegDate } from '@/entities/chats/ui/system-message';
import { log } from '@/shared/core/log';
import type { ChatMessageProps } from '../../types/chats';

type Props = Pick<ChatMessageProps, 'messageIndex'>;

export function SystemMessage({ messageIndex }: Props) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { data: messageContents } = useGetChatsByChatIdMessagesSuspenseQuery(
    {
      chatId: Number(chatId),
    },
    {
      select: (data) => {
        const message = data.data.at(messageIndex);

        if (message?.type === 'system') {
          return message.contents;
        }

        return null;
      },
    },
  );

  if (!messageContents) {
    log.error('컴포넌트 잘못 사용함');
    return null;
  }

  return messageContents.map((content) => (
    <section key={content.m_type + content.value.toString()} className="flex justify-center" aria-label="시스템 메시지">
      {match(content)
        .with({ m_type: 'date' }, (content) => <SystemMessaegDate date={content.value.text} />)
        .otherwise(() => null)}
    </section>
  ));
}
