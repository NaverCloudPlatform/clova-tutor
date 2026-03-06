/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { sampleSize } from 'es-toolkit';
import { ArrowUpRightIcon, LightbulbIcon } from 'lucide-react';
import { useMemo } from 'react';
import type { ToolInfoDto } from '@/shared/api/__generated__/dto';
import { cn } from '@/shared/utils/utils';
import { GRAMMER_QUESTION } from '../../constants/grammer-question';
import { WORD_QUESTION } from '../../constants/word-question';

type ModelMoessageRecommendationsProps = {
  tools: ToolInfoDto[];
  readonly?: boolean;
  onQuestionClick?: (question: (typeof WORD_QUESTION)[number] | (typeof GRAMMER_QUESTION)[number]) => void;
};

export function ModelMessageRecommendations({
  tools,
  readonly = false,
  onQuestionClick,
}: ModelMoessageRecommendationsProps) {
  const questionList = tools.reduce<((typeof WORD_QUESTION)[number] | (typeof GRAMMER_QUESTION)[number])[]>(
    (acc, tool) => {
      if (tool.name === 'eng_voca') {
        acc.push(...WORD_QUESTION);
      }

      if (tool.name === 'eng_grammar') {
        acc.push(...GRAMMER_QUESTION);
      }

      return acc;
    },
    [],
  );
  const sampledQuestionList = useMemo(
    () => (questionList.length >= 2 ? sampleSize(questionList, 2) : []),
    [questionList],
  );

  const handleQuestionClick = (question: (typeof WORD_QUESTION)[number] | (typeof GRAMMER_QUESTION)[number]) => {
    if (readonly) return;

    onQuestionClick?.(question);
  };

  return (
    <div className={cn('space-y-2')}>
      <h4 className="font-semibold flex items-center gap-x-1">
        <LightbulbIcon className="size-6 stroke-primary" />
        추가 질문하기
      </h4>
      <ul className="divide-y" aria-label="추가 질문 목록">
        {sampledQuestionList.map((question) => (
          <li key={question.question} className="group/question flex justify-between items-center py-3">
            <button
              type="button"
              disabled={readonly}
              className={cn(
                'w-full flex justify-between items-center text-left',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
                !readonly && 'cursor-pointer',
                readonly && 'cursor-not-allowed opacity-50',
              )}
              onClick={() => handleQuestionClick(question)}
            >
              <p className="text-sm group-hover/question:text-primary group-active/question:text-primary">
                {question.question}
              </p>
              <div className="inline-flex items-center justify-center size-6 rounded-md text-primary text-xs font-medium bg-chart-4 group-hover/question:bg-primary group-active/question:bg-primary shadow-xs transition-[color,box-shadow]">
                <ArrowUpRightIcon className="stroke-primary-foreground pointer-events-none shrink-0 size-4" />
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
