/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link } from '@tanstack/react-router';
import type { PropsWithChildren } from 'react';
import { Button } from '@/shared/ui/button';
import { ScrollArea } from '@/shared/ui/scroll-area';
import { Skeleton } from '@/shared/ui/skeleton';
import { ProblemContent } from '@/widgets/problem-book/ui/problem-content';
import { StudyMenuBar } from './_study-menu-bar';

type BookmarkedProblemContentProps = {
  problemId: string;
  chatId: number;
};

export function BookmarkedProblemContent({ problemId, chatId }: BookmarkedProblemContentProps) {
  return (
    <ProblemContent
      problemId={problemId}
      chatId={chatId}
      visibles={{
        metadata: false,
      }}
      secondaryButton={
        <Link
          from="/$subject/problems/bookmark"
          to="/$subject/chats/$chat_id/problem"
          params={{ chat_id: chatId.toString() }}
          search={{ problem_id: problemId }}
        >
          <Button size="lg" variant="outline" className="font-semibold px-5">
            채팅방에서 질문하기
          </Button>
        </Link>
      }
      studyMenuBarContent={<StudyMenuBar chatId={chatId} problemId={problemId} />}
      ProblemContentWrapper={({ children }: PropsWithChildren) => (
        <ScrollArea className="flex flex-col h-[50dvh] border rounded-md max-w-185" scrollDirection="both">
          <div className="p-5 space-y-4">{children}</div>
        </ScrollArea>
      )}
    />
  );
}

export function BookmarkedProblemContentSkeleton() {
  return (
    <div className="w-full h-full">
      <Skeleton className="h-[50dvh] w-full" />
    </div>
  );
}
