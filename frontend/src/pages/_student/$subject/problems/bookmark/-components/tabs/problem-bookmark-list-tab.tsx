/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link } from '@tanstack/react-router';
import { Suspense } from 'react';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { SUBJECT_NAMES } from '@/shared/constants/subject';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs';
import { ProblemBookmarkStatusFilter } from './_problem-bookmark-filter';
import { ProblemBookmarkList, ProblemBookmarkListSkeleton } from './_problem-bookmark-list';

export function ProblemBookmarkListTab() {
  const { subject } = useSubject();

  return (
    <Tabs value={subject}>
      <div className="flex items-center justify-between gap-x-2">
        <TabsList>
          {Object.entries(SUBJECT_NAMES).map(([subject, subjectName]) => (
            <TabsTrigger key={subject} value={subject} asChild>
              <Link key={subject} to="." params={{ subject }}>
                {subjectName}
              </Link>
            </TabsTrigger>
          ))}
        </TabsList>

        <ProblemBookmarkStatusFilter />
      </div>

      <TabsContent value={subject}>
        <Suspense fallback={<ProblemBookmarkListSkeleton />}>
          <ProblemBookmarkList subject={subject} />
        </Suspense>
      </TabsContent>
    </Tabs>
  );
}
