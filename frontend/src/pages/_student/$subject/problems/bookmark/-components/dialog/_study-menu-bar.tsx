/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link } from '@tanstack/react-router';
import { SparklesIcon } from 'lucide-react';
import { useChatStore } from '@/entities/chats/store/chats';
import { fragmentToMarkdown } from '@/packages/markdown/lib/dom-utils';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import { Button } from '@/shared/ui/button';

type StudyMenuBarProps = {
  chatId: string | number;
  problemId: string | number;
};

export function StudyMenuBar({ chatId, problemId }: StudyMenuBarProps) {
  const focus = useRichEditorStore((state) => state.focus);
  const upsertChatContent = useChatStore((state) => state.upsertChatContent);

  const handleAiQuestion = () => {
    const markdown = fragmentToMarkdown();

    upsertChatContent(Number(chatId), [
      {
        m_type: 'quote',
        value: { text: markdown, source: { type: 'problem', problem_id: String(problemId) } },
      },
      {
        m_type: 'problem_link',
        value: { problem_id: String(problemId) },
      },
    ]);
    focus();
  };

  return (
    <div className="flex space-x-1">
      <Link
        from="/$subject/problems/bookmark"
        to="/$subject/chats/$chat_id/problem"
        params={{ chat_id: chatId.toString() }}
        search={{ problem_id: problemId.toString() }}
      >
        <Button variant="ghost" size="sm" onClick={handleAiQuestion}>
          <SparklesIcon className="stroke-blue-600" />
          <span className="ai-text font-bold">AI 튜터에게 질문</span>
          <img src="/arrow-right-fill.svg" className="size-6 ml-2" role="presentation" aria-hidden />
        </Button>
      </Link>
    </div>
  );
}
