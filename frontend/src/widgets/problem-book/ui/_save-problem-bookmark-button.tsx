/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { BookmarkIcon } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import { chatsQueries, chatsQueryKeys } from '@/entities/chats/__generated__/api/queries';
import { usePatchProblemBookmarksMutation } from '@/entities/problem-bookmarks/__generated__/api/mutations';
import { problemBookmarksQueries } from '@/entities/problem-bookmarks/__generated__/api/queries';
import type { ProblemBookmarkCreateRequestBodyDto } from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog';
import { Toggle } from '@/shared/ui/toggle';

type SaveProblemBookmarkButtonProps = {
  problemId: ProblemBookmarkCreateRequestBodyDto['problem_id'];
  chatId: ProblemBookmarkCreateRequestBodyDto['chat_id'];
};

export function SaveProblemBookmarkButton({ problemId, chatId }: SaveProblemBookmarkButtonProps) {
  const queryClient = useQueryClient();
  const { data: isBookmarked } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      problemId: problemId,
      chatId: chatId,
    }),
    select: (data) => data.is_bookmarked,
  });
  const { data: isDuplicate } = useSuspenseQuery({
    ...problemBookmarksQueries.getProblemBookmarksProblemByProblemIdCheck({
      problemId: problemId,
    }),
    select: (data) => data.status === 'duplicate',
  });
  const { mutate: createProblemBookmark, isPending } = usePatchProblemBookmarksMutation({
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: chatsQueryKeys.getChatsByChatIdProblemsByProblemId.queryKey(chatId, problemId),
      });
    },
  });
  const [open, setOpen] = useState(false);

  const toggleOpen = () => setOpen((prev) => !prev);

  const saveProblemBookmark = () => {
    createProblemBookmark(
      {
        payload: {
          chat_id: chatId,
          problem_id: problemId,
          is_bookmarked: !isBookmarked,
        },
      },
      {
        onSuccess: () => {
          if (!isBookmarked) {
            toast.success('문제 저장 완료!');
          }
        },
      },
    );
  };

  const handleSaveProblemBookmark = () => {
    if (isDuplicate && !isBookmarked) {
      toggleOpen();
      return;
    }

    saveProblemBookmark();
  };

  const handleSaveDuplicateProblemBookmark = () => {
    saveProblemBookmark();
    toggleOpen();
  };

  return (
    <>
      <Toggle
        aria-label="toggle save problem bookmark"
        size="sm"
        variant="default"
        className="text-xs hover:text-accent-foreground data-[state=on]:bg-transparent data-[state=on]:*:[svg]:fill-blue-500 data-[state=on]:*:[svg]:stroke-blue-500"
        pressed={isBookmarked}
        onClick={handleSaveProblemBookmark}
      >
        <BookmarkIcon />
        {isBookmarked ? '학습 노트에 저장된 문제' : '학습 노트에 저장하기'}
      </Toggle>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent hideCloseButton>
          <DialogHeader>
            <DialogTitle>학습 노트에 이미 저장한 문제야!</DialogTitle>
            <DialogDescription>복습을 위해 한 번 더 저장할까?</DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">취소</Button>
            </DialogClose>
            <Button type="submit" onClick={handleSaveDuplicateProblemBookmark} disabled={isPending}>
              저장
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

export function SaveProblemBookmarkButtonSkeleton() {
  return (
    <Toggle
      aria-label="toggle save problem bookmark"
      size="sm"
      variant="default"
      className="text-xs hover:text-accent-foreground data-[state=on]:bg-transparent data-[state=on]:*:[svg]:fill-blue-500 data-[state=on]:*:[svg]:stroke-blue-500"
      pressed={false}
      disabled
    >
      <BookmarkIcon />
      학습 노트에 저장하기
    </Toggle>
  );
}
