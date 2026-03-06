/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useParams } from '@tanstack/react-router';
import { SparklesIcon } from 'lucide-react';
import { type SubmitHandler, useForm } from 'react-hook-form';
import { usePostGoalsMutation } from '@/entities/goals/api/mutations/use-post-goals-mutation';
import type { GoalCreateRequestBodyDto } from '@/shared/api/__generated__/dto';
import { goalCreateRequestBodyDtoSchema } from '@/shared/api/__generated__/schema';
import { Button } from '@/shared/ui/button';
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormMessage } from '@/shared/ui/form';
import { Input } from '@/shared/ui/input';

export function GoalCreateDialogContent() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const { mutate: createGoal } = usePostGoalsMutation();
  const chatGoalForm = useForm<GoalCreateRequestBodyDto>({
    mode: 'onChange',
    reValidateMode: 'onChange',
    resolver: zodResolver(
      goalCreateRequestBodyDtoSchema.extend({
        goal_count: goalCreateRequestBodyDtoSchema.shape.goal_count
          .gte(1, '1개 이상 입력해주세요.')
          .lte(10, '10개 이하로 입력해주세요.'),
      }),
    ),
    defaultValues: {
      chat_id: Number(chatId),
      goal_count: undefined,
    },
  });

  const onSubmit: SubmitHandler<GoalCreateRequestBodyDto> = (data) => {
    createGoal({
      payload: data,
    });
  };

  return (
    <DialogContent
      className="space-y-2"
      onCloseAutoFocus={(e) => {
        e.preventDefault();
        chatGoalForm.reset();
      }}
    >
      <DialogHeader>
        <DialogTitle>학습 목표 설정</DialogTitle>
        <DialogDescription className="flex items-center gap-x-2">
          <SparklesIcon className="size-4 stroke-primary" />
          함께 목표를 세우면 성취감도 두 배! 💪 오늘의 도전 문제 수를 정해볼까?
        </DialogDescription>
      </DialogHeader>

      <Form {...chatGoalForm}>
        <form
          onSubmit={(e) => {
            e.stopPropagation();
            chatGoalForm.handleSubmit(onSubmit)(e);
          }}
          className="space-y-4"
        >
          <FormField
            control={chatGoalForm.control}
            name="goal_count"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <div className="flex flex-col gap-y-2">
                    <Input
                      type="number"
                      {...field}
                      aria-label="학습 목표 개수 입력"
                      placeholder="10개까지 입력 가능해~"
                      min={0}
                      step={1}
                      value={field.value ?? ''}
                      onChange={(e) => {
                        const value = e.target.value;

                        if (value === '') {
                          // 빈 값 허용
                          field.onChange(null);
                          return;
                        }

                        // 정수만 허용 (소수점 차단)
                        const intValue = Number.parseInt(value, 10);
                        if (!Number.isNaN(intValue)) {
                          field.onChange(Math.max(0, intValue));
                        }
                      }}
                    />
                    <div className="flex gap-x-3">
                      {[2, 4, 6, 8].map((count) => (
                        <Button
                          key={count}
                          type="button"
                          variant="outline"
                          size="free"
                          className="h-8 flex-1"
                          onClick={() => field.onChange(count)}
                        >
                          {count}
                        </Button>
                      ))}
                    </div>
                  </div>
                </FormControl>
                {field.value !== null && <FormMessage />}
              </FormItem>
            )}
          />
          <DialogFooter className="justify-start">
            <DialogClose asChild>
              <Button type="submit" variant="default" disabled={!chatGoalForm.formState.isValid}>
                설정하기
              </Button>
            </DialogClose>
          </DialogFooter>
        </form>
      </Form>
    </DialogContent>
  );
}
