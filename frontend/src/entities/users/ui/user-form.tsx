/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { userCreateRequestBodyDtoSchema } from '@/shared/api/__generated__/schema';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/shared/ui/form';
import { Input } from '@/shared/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select';

const formSchema = userCreateRequestBodyDtoSchema.merge(
  z.object({
    name: userCreateRequestBodyDtoSchema.shape.name
      .trim()
      .min(1, '이름은 최소 1글자 이상이어야 합니다.')
      .max(50, '이름은 최대 50글자까지 입력 가능합니다.')
      .refine((val) => /\S/.test(val), {
        message: '이름은 공백으로만 이루어질 수 없습니다.',
      }),
  }),
);

export type UserFormData = z.infer<typeof formSchema>;

interface UserFormProps {
  defaultValues?: Partial<UserFormData>;
  onSubmit: (data: UserFormData) => void | Promise<void>;
  isSubmitting?: boolean;
  children?: React.ReactNode;
  hiddenFields?: (keyof UserFormData)[];
}

export function UserForm({
  defaultValues,
  onSubmit,
  isSubmitting = false,
  children,
  hiddenFields = [],
}: UserFormProps) {
  const form = useForm<UserFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      grade: 3,
      ...defaultValues,
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid gap-4 py-4">
          {!hiddenFields.includes('name') && (
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem className="grid grid-cols-4 items-center gap-4">
                  <FormLabel className="text-right">이름</FormLabel>
                  <div className="col-span-3">
                    <FormControl>
                      <Input placeholder="학생 이름을 입력하세요" disabled={isSubmitting} {...field} />
                    </FormControl>
                    <FormMessage />
                  </div>
                </FormItem>
              )}
            />
          )}
          {!hiddenFields.includes('grade') && (
            <FormField
              control={form.control}
              name="grade"
              render={({ field }) => (
                <FormItem className="grid grid-cols-4 items-center gap-4">
                  <FormLabel className="text-right">학년</FormLabel>
                  <div className="col-span-3">
                    <Select
                      onValueChange={(value) => field.onChange(Number.parseInt(value, 10))}
                      value={field.value.toString()}
                      disabled={isSubmitting}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="학년을 선택하세요" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="3">초등학교 3학년</SelectItem>
                        <SelectItem value="4">초등학교 4학년</SelectItem>
                        <SelectItem value="7">중학교 1학년</SelectItem>
                        <SelectItem value="10">고등학교 1학년</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </div>
                </FormItem>
              )}
            />
          )}
        </div>
        {children}
      </form>
    </Form>
  );
}

export function useUserForm() {
  return useForm<UserFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      grade: 3,
    },
  });
}
