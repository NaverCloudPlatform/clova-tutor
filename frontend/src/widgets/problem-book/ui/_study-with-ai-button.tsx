/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { CircleQuestionMarkIcon, WandIcon } from 'lucide-react';
import { useShallow } from 'zustand/shallow';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { useChatStore } from '@/entities/chats/store/chats';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import { useIsMobile } from '@/shared/hooks/use-mobile';
import { Button } from '@/shared/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/shared/ui/tooltip';
import { cn } from '@/shared/utils/utils';
import type { ProblemBookProps } from '../types/props';

type StudyWithAiButtonProps = ProblemBookProps;

export function StudyWithAiButton({ problemId, chatId }: StudyWithAiButtonProps) {
  const isMobile = useIsMobile();
  const focus = useRichEditorStore((state) => state.focus);
  const { data: imageSources } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      problemId: problemId,
      chatId: Number(chatId),
    }),
    select: (data) => {
      const problem = data.problem_info.content.problem;
      const markdownImageRegex = /!\[.*?\]\((.*?)\)/g;
      const matches = Array.from(problem.matchAll(markdownImageRegex));

      return matches.map((match) => match[1]);
    },
  });

  const selectedProblemId = useChatStore((state) => {
    const contents = state.inputMap[String(chatId)];
    if (!contents) return null;

    return contents.find((content) => content.m_type === 'problem_link') ?? null;
  });

  const { upsertChatContent, removeChatContent } = useChatStore(
    useShallow((state) => ({
      upsertChatContent: state.upsertChatContent,
      removeChatContent: state.removeChatContent,
    })),
  );

  const toggleSelectedProblemId = () => {
    if (selectedProblemId) {
      removeChatContent(Number(chatId), 'problem_link');
      return;
    }

    !isMobile && focus();

    if (imageSources) {
      upsertChatContent(Number(chatId), [
        {
          m_type: 'images',
          value: { sources: imageSources },
        },
      ]);
    }

    upsertChatContent(Number(chatId), [
      {
        m_type: 'problem_link',
        value: { problem_id: problemId },
      },
    ]);
  };

  return (
    <div className="p-1 relative">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            type="button"
            aria-label="클로바 튜터에게 문제 질문하기"
            variant="outline"
            size="free"
            className={cn(
              'size-14 p-1 rounded-full border-chart-5',
              'active:scale-95 transition-transform duration-150',
              selectedProblemId && 'ai-badge rounded-full',
            )}
            onClick={toggleSelectedProblemId}
          >
            {selectedProblemId ? (
              <img src="/icons/ai-wand.svg" alt="AI 문제 링크" className={cn('size-6 stroke-primary')} />
            ) : (
              <WandIcon className={cn('size-6 stroke-primary')} />
            )}
          </Button>
        </TooltipTrigger>

        <TooltipContent
          side="top"
          align="center"
          sideOffset={8}
          className="bg-card flex items-center gap-x-2 shadow py-3 px-4"
          arrow={false}
        >
          <CircleQuestionMarkIcon className="stroke-primary size-4.5" />
          <p className="text-sm font-medium text-foreground">클로바 튜터에게 문제 질문하기</p>
        </TooltipContent>
      </Tooltip>
    </div>
  );
}
