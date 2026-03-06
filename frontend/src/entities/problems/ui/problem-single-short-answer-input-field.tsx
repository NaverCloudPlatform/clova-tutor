/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { MathfieldElement } from 'mathlive';
import { useRef } from 'react';
import { useFormContext } from 'react-hook-form';
import { match } from 'ts-pattern';
import type { ChatProblemDetailResponseDto, SingleShortAnswerProblemResponseDto } from '@/shared/api/__generated__/dto';
import { FormControl, FormField, FormItem, FormMessage } from '@/shared/ui/form';
import { Input } from '@/shared/ui/input';
import { MathLive } from '@/shared/ui/mathlive';
import { cn } from '@/shared/utils/utils';
import { ProblemExplanation } from './problem-explanation';

type ProblemSingleShortAnswerInputFieldProps = {
  subject: SingleShortAnswerProblemResponseDto['content']['subject'];
  status: ChatProblemDetailResponseDto['status'];
  lastAnswer: ChatProblemDetailResponseDto['last_answer'];
  explanation: SingleShortAnswerProblemResponseDto['content']['explanation'];
};

export function ProblemSingleShortAnswerInputField({
  subject,
  status,
  lastAnswer,
  explanation,
}: ProblemSingleShortAnswerInputFieldProps) {
  const { register, formState, setValue } = useFormContext();
  const mathFieldRef = useRef<MathfieldElement>(null);

  const isReadOnly = status === '정답' || status === '복습 완료';

  if (isReadOnly) {
    return <ReadOnlyAnswerInput lastAnswer={lastAnswer} explanation={explanation} status={status} />;
  }

  return (
    <div className={cn('my-4')}>
      {match(subject)
        .with('math', () => {
          return (
            <FormField
              name="answer"
              disabled={isReadOnly}
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <MathLive
                      ref={mathFieldRef}
                      classNames={{
                        container: cn({
                          'border-destructive': status === '오답',
                        }),
                      }}
                      onInput={(e) => {
                        if (!(e.target instanceof MathfieldElement)) return;

                        setValue('answer', e.target.value, { shouldValidate: true, shouldDirty: true });
                      }}
                    >
                      {field.value ?? ''}
                    </MathLive>
                  </FormControl>

                  {status === '오답' && <WrongAnswerMessage submitCount={formState.submitCount} />}
                </FormItem>
              )}
            />
          );
        })
        .with('english', () => {
          return (
            <>
              <Input
                className={cn({
                  'border-destructive': status === '오답',
                })}
                placeholder="답을 입력하세요"
                {...register('answer')}
              />
              {status === '오답' && <WrongAnswerMessage submitCount={formState.submitCount} />}
            </>
          );
        })
        .otherwise(() => null)}
    </div>
  );
}

type ReadOnlyAnswerInputProps = {
  lastAnswer: ChatProblemDetailResponseDto['last_answer'];
  explanation: SingleShortAnswerProblemResponseDto['content']['explanation'];
  status: ChatProblemDetailResponseDto['status'];
};

function ReadOnlyAnswerInput({ lastAnswer, explanation, status }: ReadOnlyAnswerInputProps) {
  return (
    <div className="flex flex-col gap-y-4">
      <div className={cn('flex flex-col gap-y-2')}>
        <Input value={lastAnswer?.replaceAll('$', '')} disabled />
      </div>

      <ProblemExplanation explanation={explanation} status={status} />
    </div>
  );
}

function WrongAnswerMessage({ submitCount }: { submitCount: number }) {
  const messages = ['오답입니다.', '다시 한번 풀어보세요', '조금만 더 생각해보세요', '힌트를 참고해보세요'];
  const message = messages[submitCount % messages.length];

  return <FormMessage className="text-destructive text-xs ps-1">{message}</FormMessage>;
}
