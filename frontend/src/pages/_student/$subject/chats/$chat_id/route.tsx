/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { z } from 'zod';
import { queryClient } from '@/app/provider/tanstack-query';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { problemRestorationGuard } from '@/features/problem-restoration/lib/problem-restoration-guard';
import { StudyAreaToggleButton } from '@/pages/_student/$subject/chats/$chat_id/problem/-components/study-area-toggle-button';
import { useStudyArea } from '@/pages/_student/$subject/chats/$chat_id/problem/-hooks/use-study-area';
import { RESIZABLE_AUTO_SAVE_ID } from '@/shared/constants/storage-key';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/shared/ui/resizable';
import { ProblemSkeleton } from '@/widgets/problem-book/ui/problem-content';
import { ChatArea } from './-components/chat-area';
import { useChatStudyAreaResize } from './-hooks/use-chat-study-area-resize';

const searchSchema = z.object({
  disable_guard: z.boolean().optional(),
});

export const Route = createFileRoute('/_student/$subject/chats/$chat_id')({
  component: RouteComponent,
  validateSearch: zodValidator(searchSchema),
  beforeLoad: async (context) => {
    const redirectOptions = await problemRestorationGuard(context);

    if (redirectOptions) {
      throw redirect(redirectOptions);
    }
  },
  loader: async ({ params }) => {
    const { chat_id, subject } = params;

    try {
      const data = await queryClient.ensureQueryData({
        ...chatsQueries.getChatsByChatId({ chatId: Number(chat_id) }),
      });

      return data;
    } catch {
      const canGoBack = typeof window !== 'undefined' && window.history.length > 1;

      if (canGoBack) {
        window.history.back();

        throw redirect({
          to: '/$subject/chats',
          params: { subject },
          replace: true,
        });
      }

      throw redirect({
        to: '/$subject/chats',
        params: { subject },
        replace: true,
      });
    }
  },
  head: ({ params: { subject }, loaderData: chatData }) => {
    const titleSubfix = `${subject === 'math' ? '수학' : '영어'} 튜터`;

    const title = chatData?.title ? `${chatData.title} - ${titleSubfix}` : titleSubfix;

    return {
      meta: [
        {
          title,
        },
      ],
    };
  },
});

function RouteComponent() {
  const { isStudyAreaOpen } = useStudyArea();
  const { chatPanelProps, studyPanelProps, isResizeHandleVisible } = useChatStudyAreaResize();

  return (
    <ResizablePanelGroup direction="horizontal" autoSaveId={RESIZABLE_AUTO_SAVE_ID.CHAT_AREA}>
      <ResizablePanel {...chatPanelProps}>
        <div className="relative flex flex-col @container h-full border-t border-slate-50">
          <ChatArea />
          <div className="absolute top-1/2 right-2 -translate-y-1/2">
            <StudyAreaToggleButton />
          </div>
        </div>
      </ResizablePanel>

      {isResizeHandleVisible && <ResizableHandle className="bg-transparent" />}

      <ResizablePanel id="study-area-panel" {...studyPanelProps}>
        {isStudyAreaOpen ? <Outlet /> : <ProblemSkeleton />}
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}
