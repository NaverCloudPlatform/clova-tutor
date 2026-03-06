/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { SparklesIcon } from 'lucide-react';
import { useChatStore } from '@/entities/chats/store/chats';
import { fragmentToMarkdown } from '@/packages/markdown/lib/dom-utils';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import { Button } from '@/shared/ui/button';

type Props = {
  selectedFragment?: DocumentFragment | null;
};

export function ChatDragPopover({ selectedFragment }: Props) {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const upsertChatContent = useChatStore((state) => state.upsertChatContent);
  const focus = useRichEditorStore((state) => state.focus);

  const handleAiQuestion = () => {
    const markdown = fragmentToMarkdown(selectedFragment).trim();

    upsertChatContent(Number(chatId), [
      {
        m_type: 'quote',
        value: { text: markdown, source: { type: 'chat', chat_id: Number(chatId) } },
      },
    ]);
    focus();
  };

  return (
    <div className="flex space-x-1">
      <Button variant="ghost" size="sm" onClick={handleAiQuestion}>
        <SparklesIcon className="stroke-blue-600" />
        <span className="ai-text font-bold">AI 튜터에게 질문</span>
        <img src="/arrow-right-fill.svg" className="size-6 ml-2" role="presentation" aria-hidden />
      </Button>
    </div>
  );
}
