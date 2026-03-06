/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { CornerDownRightIcon, XIcon } from 'lucide-react';
import { useShallow } from 'zustand/shallow';
import { Button } from '@/shared/ui/button';
import { useChatStore } from '../../../entities/chats/store/chats';

export function ChatQuote() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { quote, removeChatContent } = useChatStore(
    useShallow((state) => ({
      quote: state.getChatInput(Number(chatId))?.find((content) => content.m_type === 'quote'),
      removeChatContent: state.removeChatContent,
    })),
  );

  const handleRemoveQuote = () => {
    removeChatContent(Number(chatId), 'quote');
  };

  if (!quote) return null;

  return (
    <div className="flex gap-2 bg-secondary py-2 px-3 rounded-lg justify-between">
      <div className="flex gap-3">
        <CornerDownRightIcon className="size-4 flex-shrink-0" />
        <p className="text-sm text-muted-foreground line-clamp-3">{quote.value.text}</p>
      </div>

      <Button type="button" variant="ghost" size="icon" className="size-4" onClick={handleRemoveQuote}>
        <XIcon className="size-4 flex-shrink-0" />
      </Button>
    </div>
  );
}
