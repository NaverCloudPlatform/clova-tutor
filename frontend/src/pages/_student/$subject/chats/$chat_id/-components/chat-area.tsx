/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { Suspense } from 'react';
import { StreamStatusChecker } from '@/features/chat-stream-resume/ui/stream-status-checker';
import { GoalComplete } from '@/features/goal-system/ui/goal-complete';
import { HTTP_ERROR_ACTION_CONFIG } from '@/packages/error-boundary';
import { ChatDragPopover } from '@/pages/_student/$subject/chats/$chat_id/-components/chat-drag-popover';
import { ApiErrorBoundary } from '@/shared/ui/api-error-boundary';
import { BottomScrollArea, BottomScrollAreaContent } from '@/shared/ui/bottom-scroll-area';
import { SelectionPopoverWrapper } from '@/shared/ui/selection-popover-wrapper';
import { ChatMessageList, ChatMessageListSkeleton } from '@/widgets/chat-message-list';
import { TutorChatInput } from '@/widgets/tutor-chat-input/ui/tutor-chat-input';

export function ChatArea() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });

  return (
    <ApiErrorBoundary
      overrideConfig={{
        404: {
          type: 'default',
          message: '채팅방을 찾을 수 없습니다.',
          action: HTTP_ERROR_ACTION_CONFIG.goRoot,
        },
      }}
    >
      <GoalComplete chatId={Number(chatId)} />

      <BottomScrollArea>
        <StreamStatusChecker key={chatId} />
        <div id="chat-area-content" className="flex-1 overflow-hidden w-full">
          <BottomScrollAreaContent
            classNames={{
              base: 'h-full',
            }}
          >
            <SelectionPopoverWrapper
              content={(fragment) => <ChatDragPopover selectedFragment={fragment} />}
              ignoreSelector="[data-streaming]"
            >
              <div className="p-4 @lg:max-w-3xl mx-auto">
                <Suspense fallback={<ChatMessageListSkeleton />}>
                  <ChatMessageList />
                </Suspense>
              </div>
            </SelectionPopoverWrapper>
          </BottomScrollAreaContent>
        </div>

        <div className="pb-2 px-4 bg-card rounded-b-xl @lg:max-w-3xl w-full mx-auto z-50">
          <TutorChatInput />
        </div>
      </BottomScrollArea>
    </ApiErrorBoundary>
  );
}
