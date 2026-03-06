/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Suspense } from 'react';
import { ScrollArea } from '@/shared/ui/scroll-area';
import { ProblemBottomNav, ProblemBottomNavSkeleton } from '@/widgets/problem-book/ui/_problem-bottom-nav';
import { ProblemBook } from '@/widgets/problem-book/ui/problem-book';
import { StudyAreaBlocker } from './study-area-blocker';

export function StudyArea() {
  return (
    <>
      <StudyAreaBlocker />
      <div className="flex-1 overflow-hidden relative">
        <ScrollArea className="h-full">
          <ProblemBook />
        </ScrollArea>
      </div>

      <Suspense fallback={<ProblemBottomNavSkeleton />}>
        <ProblemBottomNav />
      </Suspense>
    </>
  );
}
