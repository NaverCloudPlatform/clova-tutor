/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, redirect, useRouter } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { LoaderCircleIcon } from 'lucide-react';
import { useEffect } from 'react';
import { z } from 'zod';
import { LOCAL_STORAGE_KEY } from '@/shared/constants/storage-key';

const searchSchema = z.object({
  utm_source: z.string().optional(),
  utm_medium: z.string().optional(),
  utm_campaign: z.string().optional(),
  utm_id: z.string().optional(),
  redirect_to: z
    .string()
    .regex(/^\/(?:math|english)\/chats\/\d+$/)
    .optional(),
});

export const Route = createFileRoute('/login/$user_id')({
  component: RouteComponent,
  validateSearch: zodValidator(searchSchema),
  beforeLoad: async ({ params, search }) => {
    localStorage.setItem(LOCAL_STORAGE_KEY.USER_ID, params.user_id);

    if (search.redirect_to) {
      throw redirect({
        to: search.redirect_to,
      });
    }
  },
  head: () => {
    return {
      meta: [
        {
          title: '링크로 로그인',
        },
      ],
    };
  },
});

function RouteComponent() {
  const router = useRouter();

  useEffect(() => {
    router.navigate({ to: '/' });
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <LoaderCircleIcon className="w-10 h-10 animate-spin" />
    </div>
  );
}
