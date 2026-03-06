/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { PlusIcon, XIcon } from 'lucide-react';
import { MathfieldElement } from 'mathlive';
import { useFieldArray, useFormContext } from 'react-hook-form';
import { match } from 'ts-pattern';
import type {
  ChatProblemDetailResponseDto,
  MultipleShortAnswerProblemResponseDto,
} from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import { FormControl, FormField, FormItem, FormMessage } from '@/shared/ui/form';
import { Input } from '@/shared/ui/input';
import { MathLive } from '@/shared/ui/mathlive';
import { cn } from '@/shared/utils/utils';
import { ProblemExplanation } from './problem-explanation';

type ProblemMultipleShortAnswerInputFieldProps = {
  subject: MultipleShortAnswerProblemResponseDto['content']['subject'];
  status: ChatProblemDetailResponseDto['status'];
  lastAnswer: ChatProblemDetailResponseDto['last_answer'];
  explanation: MultipleShortAnswerProblemResponseDto['content']['explanation'];
};

export function ProblemMultipleShortAnswerInputField({
  subject,
  status,
  lastAnswer,
  explanation,
}: ProblemMultipleShortAnswerInputFieldProps) {
  const { control, formState } = useFormContext();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'answers',
  });

  const isReadOnly = status === '정답' || status === '복습 완료';

  if (isReadOnly) {
    return <ReadOnlyAnswerInputs lastAnswer={lastAnswer} explanation={explanation} status={status} />;
  }

  const handleAddField = () => {
    append({ value: '' });
  };

  const handleRemoveField = (index: number) => {
    if (fields.length > 1) {
      remove(index);
    }
  };

  return (
    <div className={cn('my-4 flex flex-col gap-y-2')}>
      {fields.map((field, index) => (
        <div key={field.id} className="flex items-center gap-x-2">
          <span className="text-sm text-muted-foreground w-6">{index + 1}.</span>
          {match(subject)
            .with('math', () => (
              <FormField
                name={`answers.${index}.value`}
                control={control}
                render={({ field: formField }) => (
                  <FormItem className="flex-1">
                    <FormControl>
                      <MathInputField
                        value={formField.value ?? ''}
                        onChange={formField.onChange}
                        hasError={status === '오답'}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            ))
            .with('english', () => (
              <FormField
                name={`answers.${index}.value`}
                control={control}
                render={({ field: formField }) => (
                  <FormItem className="flex-1">
                    <FormControl>
                      <Input
                        className={cn({
                          'border-destructive': status === '오답',
                        })}
                        placeholder={`답 ${index + 1}`}
                        value={formField.value ?? ''}
                        onChange={formField.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            ))
            .otherwise(() => null)}

          {fields.length > 1 && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-8 shrink-0"
              onClick={() => handleRemoveField(index)}
            >
              <XIcon className="size-4" />
            </Button>
          )}
        </div>
      ))}

      <Button type="button" variant="outline" size="sm" className="w-fit mt-1" onClick={handleAddField}>
        <PlusIcon className="size-4 mr-1" />답 추가
      </Button>

      {status === '오답' && <WrongAnswerMessage submitCount={formState.submitCount} />}
    </div>
  );
}

type MathInputFieldProps = {
  value: string;
  onChange: (value: string) => void;
  hasError: boolean;
};

function MathInputField({ value, onChange, hasError }: MathInputFieldProps) {
  const handleInput = (e: React.FormEvent<MathfieldElement>) => {
    if (!(e.target instanceof MathfieldElement)) return;
    onChange(e.target.value);
  };

  return (
    <MathLive
      classNames={{
        container: cn({
          'border-destructive': hasError,
        }),
      }}
      onInput={handleInput}
    >
      {value}
    </MathLive>
  );
}

type ReadOnlyAnswerInputsProps = {
  lastAnswer: ChatProblemDetailResponseDto['last_answer'];
  explanation: MultipleShortAnswerProblemResponseDto['content']['explanation'];
  status: ChatProblemDetailResponseDto['status'];
};

function ReadOnlyAnswerInputs({ lastAnswer, explanation, status }: ReadOnlyAnswerInputsProps) {
  const answers = parseLastAnswers(lastAnswer);

  return (
    <div className="flex flex-col gap-y-4">
      <div className={cn('flex flex-col gap-y-2')}>
        {answers.map((answer, index) => (
          <div key={index} className="flex items-center gap-x-2">
            <span className="text-sm text-muted-foreground w-6">{index + 1}.</span>
            <Input value={answer.replaceAll('$', '')} disabled className="flex-1" />
          </div>
        ))}
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

function parseLastAnswers(lastAnswer: ChatProblemDetailResponseDto['last_answer']): string[] {
  if (!lastAnswer) return [];

  try {
    const parsed = JSON.parse(lastAnswer);
    if (Array.isArray(parsed)) {
      return parsed.map(String);
    }
  } catch {
    return [lastAnswer];
  }

  return [];
}
