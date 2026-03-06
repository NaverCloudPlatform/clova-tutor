/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useBlocker, useParams } from '@tanstack/react-router';
import { compact } from 'es-toolkit';
import { Suspense } from 'react';
import { useShallow } from 'zustand/shallow';
import { useChatInputMapKey } from '@/entities/chats/hooks/use-chat-input-map-key';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { useChatStore } from '@/entities/chats/store/chats';
import { GoalProgressStatus, GoalProgressStatusSkeleton } from '@/entities/goals/ui/goal-progress-status';
import { GoalToggleDialogButton, GoalToggleDialogSkeleton } from '@/features/goal-system/ui/goal-toggle-dialog-button';
import { MathBlockButton } from '@/features/latex-input/ui/math-block-button';
import { RichEditor } from '@/packages/rich-editor';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import type { ChatMessageCreateRequestBodyDto } from '@/shared/api/__generated__/dto';
import { ScrollArea } from '@/shared/ui/scroll-area';
import { cn } from '@/shared/utils/utils';
import { ChatQuote } from '@/widgets/tutor-chat-input/ui/chat-quote';
import { ClipboardUploadWrapper } from './clipboard-upload-wrapper';
import { FileUploadButton } from './file-upload-button';
import { ProblemLinkChip } from './problem-link-chip';
import { TutorChatInputFormButton } from './tutor-chat-input-form-button';
import { ActiveGoalsPlaceholder, ActiveGoalsPlaceholderSkeleton } from './tutor-chat-input-placeholder';
import { UploadFilePreview } from './upload-file-preview';

type Props = {
  onSubmit: (payload: ChatMessageCreateRequestBodyDto) => void;
};

export function TutorChatInputForm({ onSubmit }: Props) {
  const { chat_id: chatId } = useParams({
    strict: false,
  });
  const { isStreaming } = useChatStreamMutationState({
    chatId: Number(chatId),
  });
  const getText = useRichEditorStore((state) => state.getText);
  const inputMapKey = useChatInputMapKey();
  const {
    getChatInput,
    savedChatInput,
    upsertChatContent,
    removeChatInput,
    removeEmptyContent,
    removeEmptyChatInput,
    selectedProblemId,
  } = useChatStore(
    useShallow((state) => ({
      getChatInput: state.getChatInput,
      savedChatInput: state.getChatInput(inputMapKey),
      upsertChatContent: state.upsertChatContent,
      removeChatInput: state.removeChatInput,
      removeEmptyContent: state.removeEmptyContent,
      removeEmptyChatInput: state.removeEmptyChatInput,
      selectedProblemId: state.getChatInput(inputMapKey)?.find((content) => content.m_type === 'problem_link')?.value
        .problem_id,
    })),
  );
  const defaultTextValue = getChatInput(inputMapKey)?.find((content) => content.m_type === 'text')?.value.text;

  useBlocker({
    shouldBlockFn: () => {
      const text = getText();
      const content = [
        {
          m_type: 'text' as const,
          value: { text },
        },
      ];

      if (text) {
        upsertChatContent(inputMapKey, content);
      }

      const isMobile = window.innerWidth < 768;
      removeEmptyContent(inputMapKey, { keepTypes: isMobile ? ['problem_link'] : undefined });
      removeEmptyChatInput(inputMapKey);

      return false;
    },
    enableBeforeUnload: false,
  });

  const sendMessage = () => {
    const text = getText().trim();

    if (!text) return;

    const payload = {
      contents: compact([...(savedChatInput ?? []), { m_type: 'text' as const, value: { text } }]),
      metadata: {},
    };

    onSubmit(payload);
    removeChatInput(inputMapKey);

    // 모바일 키패드 내리기
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (isStreaming) return;

    sendMessage();
  };

  return (
    <div className={cn('flex flex-col space-y-1')}>
      <form onSubmit={handleSubmit}>
        <div
          className={cn(
            'flex flex-col space-y-4 p-2 h-full bg-popover rounded-xl border border-border -mt-2',
            selectedProblemId && 'ai-badge bg-none!',
          )}
        >
          <div className="space-y-1">
            {chatId && <ChatQuote />}

            <UploadFilePreview />

            <ClipboardUploadWrapper>
              <RichEditor
                className="min-h-13 max-h-120 border-0 shadow-none focus-visible:ring-0 px-2 py-1 overflow-y-scroll"
                defaultValue={defaultTextValue}
              >
                {chatId ? (
                  <Suspense fallback={<ActiveGoalsPlaceholderSkeleton />}>
                    <ActiveGoalsPlaceholder />
                  </Suspense>
                ) : (
                  '궁금한 것이 있다면 언제든 물어봐!'
                )}
              </RichEditor>
            </ClipboardUploadWrapper>
          </div>

          <div className="flex flex-col w-full min-w-0">
            <div className="flex items-center w-full gap-x-2 min-w-0">
              <div className="flex items-center min-w-0 flex-1 gap-x-2">
                <div className="flex items-center space-x-1.5 shrink-0">
                  <FileUploadButton />
                  <MathBlockButton />
                  {chatId && (
                    <Suspense fallback={<GoalToggleDialogSkeleton />}>
                      <GoalToggleDialogButton />
                    </Suspense>
                  )}
                </div>

                <ScrollArea
                  scrollDirection="horizontal"
                  className="flex-1 @lg:flex-none min-w-0"
                  componentProps={{
                    viewport: {
                      className: '!overflow-x-auto',
                    },
                  }}
                >
                  <div className="flex items-center space-x-2 min-w-max">
                    {chatId && (
                      <div className="shrink-0">
                        <Suspense fallback={<GoalProgressStatusSkeleton />}>
                          <GoalProgressStatus chatId={Number(chatId)} />
                        </Suspense>
                      </div>
                    )}
                    <div className="shrink-0">
                      <ProblemLinkChip />
                    </div>
                  </div>
                </ScrollArea>
              </div>

              <div className="shrink-0">
                <TutorChatInputFormButton />
              </div>
            </div>
          </div>
        </div>
      </form>
      <p className="text-xs text-foreground-weak text-center mt-1.5">
        클로바 튜터는 학습에 관한 정보 제공 시 실수를 할 수 있으니, 중요한 정보는 다시 한번 확인하세요.
      </p>
    </div>
  );
}
