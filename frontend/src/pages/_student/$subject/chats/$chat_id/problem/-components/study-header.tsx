/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ChevronLeftIcon, GraduationCapIcon, XIcon } from 'lucide-react';
import { Suspense } from 'react';
import {
  ProblemNavigatorDropdown,
  ProblemNavigatorDropdownSkeleton,
} from '@/pages/_student/$subject/chats/$chat_id/problem/-components/_problem-list-dropdown';
import { useStudyArea } from '@/pages/_student/$subject/chats/$chat_id/problem/-hooks/use-study-area';
import { useIsMobile } from '@/shared/hooks/use-mobile';
import { Button } from '@/shared/ui/button';

export function StudyHeader() {
  const { closeStudyArea } = useStudyArea();
  const isMobile = useIsMobile();

  const handleCloseStudyArea = () => {
    closeStudyArea();
  };

  return isMobile ? (
    <MobileStudyHeader onCloseStudyArea={handleCloseStudyArea} />
  ) : (
    <DesktopStudyHeader onCloseStudyArea={handleCloseStudyArea} />
  );
}

export type TStudyHeaderProps = {
  onCloseStudyArea: () => void;
};

function DesktopStudyHeader({ onCloseStudyArea }: TStudyHeaderProps) {
  return (
    <header className="flex h-13 shrink-0 items-center justify-between ps-5 gap-2 border-b transition-[width,height] ease-linear">
      <div className="flex items-center gap-2 w-full">
        <GraduationCapIcon className="size-5" />
        <h2 className="text-base font-semibold whitespace-nowrap">학습 문제 추천</h2>

        <Suspense fallback={<ProblemNavigatorDropdownSkeleton />}>
          <ProblemNavigatorDropdown />
        </Suspense>
      </div>

      <div className="p-2">
        <Button variant="ghost" size="icon" className="rounded-full" onClick={onCloseStudyArea}>
          <XIcon className="stroke-muted-foreground" aria-label="추천 문제 영역 닫기" />
        </Button>
      </div>
    </header>
  );
}

function MobileStudyHeader({ onCloseStudyArea }: TStudyHeaderProps) {
  return (
    <header className="flex h-13 shrink-0 items-center justify-between p-2 pe-4 gap-2 border-b transition-[width,height] ease-linear">
      <Button variant="ghost" size="icon" className="rounded-full" onClick={onCloseStudyArea}>
        <ChevronLeftIcon className="stroke-muted-foreground" aria-label="추천 문제 영역 닫기" />
      </Button>

      <Suspense fallback={<ProblemNavigatorDropdownSkeleton />}>
        <ProblemNavigatorDropdown />
      </Suspense>
    </header>
  );
}
