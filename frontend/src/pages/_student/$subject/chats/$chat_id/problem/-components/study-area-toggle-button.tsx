/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { useParams } from '@tanstack/react-router';
import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { withErrorBoundary } from '@/shared/hoc/with-error-boundary';
import { withSuspense } from '@/shared/hoc/with-suspense';
import { Button } from '@/shared/ui/button';
import { useStudyArea } from '../-hooks/use-study-area';

export const StudyAreaToggleButton = withErrorBoundary(
  withSuspense(() => {
    const { chat_id: chatId } = useParams({
      from: '/_student/$subject/chats/$chat_id',
    });
    const { data: problems } = useSuspenseQuery({
      ...chatsQueries.getChatsByChatIdProblems({
        chatId: Number(chatId),
      }),
    });
    const { isStudyAreaOpen, toggleStudyArea } = useStudyArea();

    const handleClick = () => {
      toggleStudyArea();
    };

    if (!problems || problems?.length === 0) return null;

    return (
      <Button variant="outline" size="icon" aria-label="문제 추천 영역 토글" onClick={handleClick}>
        {isStudyAreaOpen ? <ChevronRightIcon className="w-4 h-4" /> : <ChevronLeftIcon className="w-4 h-4" />}
      </Button>
    );
  }),
);
