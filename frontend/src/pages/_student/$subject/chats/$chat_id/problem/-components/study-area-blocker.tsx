/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { useBlocker, useParams } from '@tanstack/react-router';
import { Suspense, useState } from 'react';
import { match } from 'ts-pattern';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useProblemStore } from '@/entities/problems/store/problem';
import { useIsMobile } from '@/shared/hooks/use-mobile';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/shared/ui/alert-dialog';

export function StudyAreaBlocker() {
  const isMobile = useIsMobile();

  if (isMobile) return null;

  return (
    <Suspense fallback={null}>
      <StudyAreaBlockerContent />
    </Suspense>
  );
}

function StudyAreaBlockerContent() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id/problem',
  });
  const resetLastProblemId = useProblemStore((state) => state.resetLastProblemId);
  const { data: problems } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblems({
      chatId: Number(chatId),
    }),
  });
  const [open, setOpen] = useState(false);
  const isUnGradedProblemExsist = problems.some((problem) => problem.status === '풀지 않음');

  const { proceed, reset } = useBlocker({
    shouldBlockFn: ({ next }) => {
      if ('disable_guard' in next.search && next.search.disable_guard) {
        return false;
      }

      return match(next)
        .with(
          {
            routeId: '/_student/$subject/chats/$chat_id',
            params: { chat_id: chatId },
          },
          () => {
            if (isUnGradedProblemExsist) {
              setOpen(true);
              return true;
            }

            resetLastProblemId(Number(chatId));
            return false;
          },
        )
        .otherwise(() => {
          return false;
        });
    },
    enableBeforeUnload: false,
    withResolver: true,
  });

  const handleCancel = () => {
    reset?.();
  };

  const handleConfirm = () => {
    setOpen(false);
    resetLastProblemId(Number(chatId));
    proceed?.();
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>풀지 않은 문제가 있어요</AlertDialogTitle>
          <AlertDialogDescription>이대로 문제 풀기를 종료하시겠어요?</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={handleCancel}>취소</AlertDialogCancel>
          <AlertDialogAction onClick={handleConfirm}>종료하기</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
