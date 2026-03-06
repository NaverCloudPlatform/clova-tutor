/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link, useParams } from '@tanstack/react-router';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';
import { cn } from '@/shared/utils/utils';

type ChatTitleProps = {
  chat: ChatResponseDto;
  classNames?: {
    title?: string;
    icon?: string;
  };
} & React.ComponentProps<'a'>;

export function ChatTitle({ chat, classNames, className, ...props }: ChatTitleProps) {
  const { chat_id: currentChatId } = useParams({
    strict: false,
  });
  const { isStreaming } = useChatStreamMutationState({
    chatId: chat.id,
  });

  const serach = Number(currentChatId) === chat.id ? { disable_guard: true } : ({} as const);

  return (
    <Link
      to={`/$subject/chats/$chat_id`}
      params={{
        subject: chat.subject === 'math' ? 'math' : 'english',
        chat_id: String(chat.id),
      }}
      search={serach}
      className={cn(
        className,
        chat.title === '' && 'animate-pulse bg-cool-gray-300 data-[active=true]:bg-cool-gray-300 h-6 rounded',
      )}
      {...props}
    >
      <p className={cn('line-clamp-1 break-all', isStreaming && 'animate-pulse', classNames?.title)}>{chat.title}</p>
    </Link>
  );
}
