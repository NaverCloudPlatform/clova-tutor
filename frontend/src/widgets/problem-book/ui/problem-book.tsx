/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams, useSearch } from '@tanstack/react-router';
import { Suspense } from 'react';
import { SaveProblemBookmarkButton, SaveProblemBookmarkButtonSkeleton } from './_save-problem-bookmark-button';
import { StudyWithAiButton } from './_study-with-ai-button';
import { ProblemContent, ProblemSkeleton } from './problem-content';

export function ProblemBook() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id/problem',
  });
  const { problem_id: problemId } = useSearch({
    from: '/_student/$subject/chats/$chat_id/problem',
  });

  return (
    <div className="flex flex-col w-full h-full space-y-4 p-4">
      <div className="relative flex-1 h-full flex flex-col justify-between w-full space-y-2">
        <div className="flex justify-start">
          <Suspense fallback={<SaveProblemBookmarkButtonSkeleton />}>
            <SaveProblemBookmarkButton problemId={problemId} chatId={Number(chatId)} />
          </Suspense>
        </div>

        <Suspense fallback={<ProblemSkeleton />}>
          <ProblemContent
            key={problemId}
            problemId={problemId}
            chatId={Number(chatId)}
            secondaryButton={<StudyWithAiButton problemId={problemId} chatId={Number(chatId)} />}
          />
        </Suspense>
      </div>
    </div>
  );
}
