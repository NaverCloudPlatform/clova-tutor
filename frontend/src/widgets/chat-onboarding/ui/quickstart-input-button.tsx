/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useShallow } from 'zustand/shallow';
import { useChatInputMapKey } from '@/entities/chats/hooks/use-chat-input-map-key';
import { useChatStore } from '@/entities/chats/store/chats';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import { Button } from '@/shared/ui/button';

type OnboardingQuickstartButtonProps = {
  prompt: string;
  questionNumber: number;
};

export function OnboardingQuickstartButton({ prompt, questionNumber }: OnboardingQuickstartButtonProps) {
  const { deleteAll, insertText } = useRichEditorStore(
    useShallow((state) => ({
      deleteAll: state.deleteAll,
      insertText: state.insertText,
    })),
  );
  const inputMapKey = useChatInputMapKey();
  const { removeChatContent } = useChatStore(
    useShallow((state) => ({
      removeChatContent: state.removeChatContent,
    })),
  );

  const handleClick = async () => {
    deleteAll();
    insertText(prompt);
    removeChatContent(inputMapKey, 'images');
  };

  return (
    <Button
      variant="secondary"
      size="free"
      className="flex flex-col items-start justify-between gap-y-3 px-5 py-4 sm:min-h-42 min-h-24 cursor-pointer w-full"
      onClick={handleClick}
    >
      <div className="flex items-center gap-x-2">
        <p className="font-bold whitespace-pre-wrap wrap-break-word">Q{questionNumber}</p>
      </div>
      <p className="wrap-break-word whitespace-pre-wrap text-left flex-1" data-testid="onboarding-prompt">
        {prompt}
      </p>
    </Button>
  );
}
