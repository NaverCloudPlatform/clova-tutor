/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { z } from 'zod';
import { useChatStore } from '@/entities/chats/store/chats';
import { useProblemStore } from '@/entities/problems/store/problem';
import { HTTP_ERROR_ACTION_CONFIG } from '@/packages/error-boundary';
import { ApiErrorBoundary } from '@/shared/ui/api-error-boundary';
import { StudyArea } from './-components/study-area';
import { StudyHeader } from './-components/study-header';

const searchSchema = z.object({
  problem_id: z.string(),
});

export const Route = createFileRoute('/_student/$subject/chats/$chat_id/problem')({
  component: RouteComponent,
  validateSearch: zodValidator(searchSchema),
  loaderDeps: ({ search }) => ({ problem_id: search.problem_id }),
  loader: ({ params, deps }) => {
    const { chat_id } = params;
    const { problem_id } = deps;

    const { upsertChatContent } = useChatStore.getState();
    const { setLastProblemId } = useProblemStore.getState();
    upsertChatContent(Number(chat_id), [
      {
        m_type: 'problem_link',
        value: { problem_id },
      },
    ]);
    setLastProblemId(Number(chat_id), problem_id);
  },
});

function RouteComponent() {
  return (
    <article className="flex-1/2 flex flex-col relative h-full">
      <ApiErrorBoundary
        overrideConfig={{
          404: {
            type: 'default',
            message: '문제를 찾을 수 없습니다.',
            action: HTTP_ERROR_ACTION_CONFIG.goBack,
          },
        }}
      >
        <StudyHeader />
        <StudyArea />
      </ApiErrorBoundary>
    </article>
  );
}

type SearchSchema = z.infer<typeof searchSchema>;

export { searchSchema as studentChatProblemSearchSchema, type SearchSchema as StudentChatProblemSearchSchema };
