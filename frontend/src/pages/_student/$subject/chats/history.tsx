/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, Link } from '@tanstack/react-router';
import { PenLineIcon, SquarePenIcon } from 'lucide-react';
import { Suspense } from 'react';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { SUBJECT_NAMES } from '@/shared/constants/subject';
import type { Subject } from '@/shared/types/common';
import { Button } from '@/shared/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs';
import { ChatHistoryList, ChatHistoryListSkeleton } from '@/widgets/chat-history-list/ui/chat-history-list';

export const Route = createFileRoute('/_student/$subject/chats/history')({
  component: RouteComponent,
  head: ({ params: { subject } }) => {
    const title = `${subject === 'math' ? '수학' : '영어'} 채팅 기록`;

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
  const { subject } = useSubject();

  return (
    <div className="flex flex-col gap-y-14 @container h-full overflow-y-auto pt-12">
      <div className="flex flex-col gap-y-8 w-full mx-auto @lg:max-w-3xl px-5">
        <div className="flex items-center justify-between gap-x-2">
          <h1 className="flex items-center gap-x-2 text-3xl font-bold">
            <PenLineIcon className="size-8 stroke-primary" />
            채팅 기록
          </h1>

          <Link from="/$subject/chats/history" to="/$subject/chats">
            <Button>
              <SquarePenIcon />새 채팅
            </Button>
          </Link>
        </div>

        <Tabs value={subject}>
          <TabsList>
            {Object.entries(SUBJECT_NAMES).map(([subject, subjectName]) => (
              <TabsTrigger key={subject} value={subject} asChild>
                <Link key={subject} to="." params={{ subject }}>
                  {subjectName}
                </Link>
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent key={subject} value={subject}>
            <Suspense fallback={<ChatHistoryListSkeleton />}>
              <ChatHistoryList subject={subject as Subject} />
            </Suspense>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
