/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link } from '@tanstack/react-router';
import { format } from 'date-fns';
import { InfoIcon } from 'lucide-react';
import { Suspense } from 'react';
import { ProblemMetadataBadge } from '@/entities/problems/ui/problem-metadata-badge';
import { ProblemReadOnly } from '@/entities/problems/ui/problem-readonly';
import { ProblemStatusBadge } from '@/entities/problems/ui/problem-status-badge';
import type { ProblemBookmarkResponseDto } from '@/shared/api/__generated__/dto';
import { Item, ItemContent, ItemMedia, ItemTitle } from '@/shared/ui/item';
import { ScrollArea } from '@/shared/ui/scroll-area';
import { ProblemBookmarkToggleButton, ProblemBookmarkToggleButtonSkeleton } from './_problem-bookmark-toggle-button';

type ProblemBookmarkItemProps = {
  bookmarkedProblem: ProblemBookmarkResponseDto;
};

export function ProblemBookmarkItem({ bookmarkedProblem }: ProblemBookmarkItemProps) {
  const isGoalCalloutVisible =
    bookmarkedProblem.chat.has_active_goal && ['풀지 않음', '오답'].includes(bookmarkedProblem.problem.status);

  return (
    <Link
      to="."
      params={{
        subject: bookmarkedProblem.problem.problem_info.content.subject,
      }}
      search={(prev) => ({
        ...prev,
        modal: {
          type: 'bookmarked-problem',
          chatId: bookmarkedProblem.chat.id,
          problemId: bookmarkedProblem.problem.problem_info.id,
        },
      })}
    >
      <div className="h-full border rounded-md bg-card space-y-2 flex flex-col">
        <div className="flex justify-end pt-2 pr-2">
          <ProblemStatusBadge status={bookmarkedProblem.problem.status} className="size-6" />
        </div>

        <div className="relative flex-1">
          <ScrollArea>
            <div className="px-3 text-[0.75rem] h-48">
              <ProblemReadOnly problem={bookmarkedProblem.problem.problem_info} hideMetadata />
            </div>
          </ScrollArea>

          {isGoalCalloutVisible && (
            <Item className="absolute bottom-0 left-2 right-2 bg-blue-50 px-3 py-2 gap-x-2">
              <ItemMedia>
                <InfoIcon className="stroke-primary size-4" />
              </ItemMedia>
              <ItemContent className="">
                <ItemTitle className="text-sm font-normal text-primary">
                  <p>
                    이 문제를 풀고 <b>학습 목표</b>에 한걸음 다가가볼까?
                  </p>
                </ItemTitle>
              </ItemContent>
            </Item>
          )}
        </div>

        <div className="flex items-start justify-between bg-secondary p-4 rounded-b-md mt-auto">
          <div className="flex flex-col gap-y-2 ">
            <p className="text-xs text-secondary-foreground">
              {format(new Date(bookmarkedProblem.bookmarked_at), 'yyyy-MM-dd')}
            </p>

            <ProblemMetadataBadge
              grade={bookmarkedProblem.problem.problem_info.content.grade}
              level={bookmarkedProblem.problem.problem_info.content.level}
              category={bookmarkedProblem.problem.problem_info.content.category}
              classNames={{
                star: 'size-3',
                text: 'text-sm text-foreground font-semibold',
              }}
            />
          </div>

          <Suspense fallback={<ProblemBookmarkToggleButtonSkeleton />}>
            <ProblemBookmarkToggleButton
              problemId={bookmarkedProblem.problem.problem_info.id}
              chatId={bookmarkedProblem.chat.id}
              bookmarkedAt={bookmarkedProblem.bookmarked_at}
            />
          </Suspense>
        </div>
      </div>
    </Link>
  );
}
