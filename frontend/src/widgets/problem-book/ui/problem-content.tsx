/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useSuspenseQuery } from '@tanstack/react-query';
import type { PropsWithChildren } from 'react';
import { useForm } from 'react-hook-form';
import { match } from 'ts-pattern';
import { z } from 'zod';
import { usePostChatsByChatIdProblemsByProblemIdSubmitMutation } from '@/entities/chats/__generated__/api/mutations';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { ProblemHint } from '@/entities/problems/ui/problem-hint';
import { ProblemMetadataBadge } from '@/entities/problems/ui/problem-metadata-badge';
import { ProblemMultipleChoiceOptions } from '@/entities/problems/ui/problem-multiple-choice-options';
import { ProblemMultipleShortAnswerInputField } from '@/entities/problems/ui/problem-multiple-short-answer-input-field';
import { ProblemQuestion } from '@/entities/problems/ui/problem-question';
import { ProblemSingleChoiceOptions } from '@/entities/problems/ui/problem-single-choice-options';
import { ProblemSingleShortAnswerInputField } from '@/entities/problems/ui/problem-single-short-answer-input-field';
import { Form, FormControl, FormField, FormItem } from '@/shared/ui/form';
import { SelectionPopoverWrapper } from '@/shared/ui/selection-popover-wrapper';
import { Skeleton } from '@/shared/ui/skeleton';
import { cn } from '@/shared/utils/utils';
import type { ProblemBookProps } from '../types/props';
import { CheckAnswerButton } from './_check-answer-button';
import { StudyMenuBar } from './_study-menu-bar';

function DefaultProblemContentWrapper({ children }: PropsWithChildren) {
  return <div className="flex flex-col">{children}</div>;
}

type ProblemContentProps = ProblemBookProps & {
  secondaryButton?: React.ReactNode;
  visibles?: {
    metadata?: boolean;
  };
  studyMenuBarContent?: React.ReactNode;
  ProblemContentWrapper?: React.ComponentType<PropsWithChildren>;
};

export function ProblemContent({
  problemId,
  chatId,
  secondaryButton,
  visibles = {
    metadata: true,
  },
  studyMenuBarContent,
  ProblemContentWrapper,
}: ProblemContentProps) {
  const { data: problem } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdProblemsByProblemId({
      problemId: problemId,
      chatId: Number(chatId),
    }),
  });

  const { mutate: submitAnswer, isPending } = usePostChatsByChatIdProblemsByProblemIdSubmitMutation();

  type FormValues = {
    answer?: string | number | number[];
    answers?: { value: string }[];
  };

  const getDefaultValues = (): FormValues => {
    if (problem.problem_info.type === '다중선택 객관식') {
      if (!problem.last_answer) return { answer: [] };
      try {
        const parsed = JSON.parse(problem.last_answer);
        return { answer: Array.isArray(parsed) ? parsed.map(Number) : [] };
      } catch {
        return { answer: [] };
      }
    }
    if (problem.problem_info.type === '다중응답 주관식') {
      if (!problem.last_answer) return { answers: [{ value: '' }] };
      try {
        const parsed = JSON.parse(problem.last_answer);
        if (Array.isArray(parsed)) {
          return { answers: parsed.map((v) => ({ value: String(v).replaceAll('$', '').trim() })) };
        }
      } catch {
        return { answers: [{ value: '' }] };
      }
      return { answers: [{ value: '' }] };
    }
    return { answer: problem.last_answer ?? undefined };
  };

  const formSchema = z.object({
    answer: z.union([z.number(), z.string(), z.array(z.number())]).optional(),
    answers: z.array(z.object({ value: z.string() })).optional(),
  });

  const form = useForm<FormValues>({
    defaultValues: getDefaultValues(),
    resolver: zodResolver(formSchema),
  });

  const handleSubmit = form.handleSubmit((data) => {
    if (isPending) return;

    const submitData = match(problem.problem_info)
      .with({ type: '단일선택 객관식' }, () => ({
        type: '단일선택 객관식' as const,
        answer: Number(data.answer),
      }))
      .with({ type: '다중선택 객관식' }, () => ({
        type: '다중선택 객관식' as const,
        answer: data.answer as number[],
      }))
      .with({ type: '단일응답 주관식' }, (problemInfo) => ({
        type: '단일응답 주관식' as const,
        answer: problemInfo.content.subject === 'math' ? `$ ${data.answer} $` : String(data.answer),
      }))
      .with({ type: '다중응답 주관식' }, (problemInfo) => ({
        type: '다중응답 주관식' as const,
        answer: (data.answers ?? [])
          .filter((item) => item.value.trim() !== '')
          .map((item) => (problemInfo.content.subject === 'math' ? `$ ${item.value} $` : item.value)),
      }))
      .otherwise(() => null);

    if (submitData) {
      submitAnswer({
        problemId: problemId,
        chatId: Number(chatId),
        payload: {
          answer: submitData,
        },
      });
    }
  });

  const isReadOnly = problem.status === '정답' || problem.status === '복습 완료';
  const isHintVisible = problem.status !== '풀지 않음';
  const ProblemContentWrapperFinal = ProblemContentWrapper ?? DefaultProblemContentWrapper;

  return (
    <div className="px-1 flex-1 h-full space-y-3">
      <Form {...form}>
        <form onSubmit={handleSubmit} className={cn('h-full flex flex-col')}>
          <div className={cn('flex flex-col gap-y-4')}>
            <ProblemContentWrapperFinal>
              {visibles?.metadata && (
                <ProblemMetadataBadge
                  grade={problem.problem_info.content.grade}
                  level={problem.problem_info.content.level}
                  category={problem.problem_info.content.category}
                />
              )}
              <SelectionPopoverWrapper
                content={(fragment) =>
                  studyMenuBarContent ?? (
                    <StudyMenuBar chatId={chatId} problemId={problemId} selectedFragment={fragment} />
                  )
                }
              >
                <ProblemQuestion problem={`${problem.number}. ${problem.problem_info.content.problem}`} />
              </SelectionPopoverWrapper>

              {isHintVisible && <ProblemHint hint={problem.problem_info.content.hint} />}

              {match(problem.problem_info)
                .with({ type: '단일선택 객관식' }, (problemInfo) => (
                  <FormField
                    name="answer"
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <ProblemSingleChoiceOptions
                            lastAnswer={problem.last_answer}
                            status={problem.status}
                            explanation={problemInfo.content.explanation}
                            choices={problemInfo.content.choices}
                            value={field.value}
                            onChange={field.onChange}
                            isReadOnly={isReadOnly}
                            chatId={Number(chatId)}
                            problemId={problemId}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                ))
                .with({ type: '다중선택 객관식' }, (problemInfo) => (
                  <FormField
                    name="answer"
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <ProblemMultipleChoiceOptions
                            lastAnswer={problem.last_answer}
                            status={problem.status}
                            explanation={problemInfo.content.explanation}
                            choices={problemInfo.content.choices}
                            value={field.value as number[]}
                            onChange={field.onChange}
                            isReadOnly={isReadOnly}
                            chatId={Number(chatId)}
                            problemId={problemId}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                ))
                .with({ type: '단일응답 주관식' }, (problemInfo) => (
                  <ProblemSingleShortAnswerInputField
                    subject={problemInfo.content.subject}
                    status={problem.status}
                    lastAnswer={problem.last_answer}
                    explanation={problemInfo.content.explanation}
                  />
                ))
                .with({ type: '다중응답 주관식' }, (problemInfo) => (
                  <ProblemMultipleShortAnswerInputField
                    subject={problemInfo.content.subject}
                    status={problem.status}
                    lastAnswer={problem.last_answer}
                    explanation={problemInfo.content.explanation}
                  />
                ))
                .otherwise(() => null)}
            </ProblemContentWrapperFinal>
          </div>

          <div className="flex items-center self-end gap-x-3 py-4">
            {secondaryButton}

            <CheckAnswerButton problemId={problemId} chatId={Number(chatId)} />
          </div>
        </form>
      </Form>
    </div>
  );
}

export function ProblemSkeleton() {
  return (
    <div className="px-1 flex-1">
      <div className="flex flex-col gap-y-4">
        <div className="flex flex-col gap-y-2">
          <Skeleton className="h-7 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
        <div className="flex flex-col gap-y-2">
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
        </div>
      </div>
    </div>
  );
}
