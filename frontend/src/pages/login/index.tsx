/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { z } from 'zod';
import { AddUserDialog } from '@/features/user-management/ui/add-user-dialog';
import { LOCAL_STORAGE_KEY } from '@/shared/constants/storage-key';
import { useWindowNavigationIntercept } from '@/shared/hooks/use-window-navigation-intercpet';
import { UserInput } from '@/widgets/user-management/ui/user-input';
import { UserTable } from '@/widgets/user-management/ui/user-table';

const searchSchema = z.object({
  username: z.string().optional(),
});

export const Route = createFileRoute('/login/')({
  validateSearch: zodValidator(searchSchema),
  component: LoginPage,
  head: () => {
    return {
      meta: [
        {
          title: '로그인',
        },
      ],
    };
  },
});

function LoginPage() {
  useWindowNavigationIntercept({
    shouldIntercept: (url) => {
      const isLoginPath = url.pathname === '/login' || url.pathname === '/login/';
      return !localStorage.getItem(LOCAL_STORAGE_KEY.USER_ID) && !isLoginPath;
    },
  });

  return (
    <div className="bg-secondary px-4 py-8 min-h-svh">
      <div className="max-w-5xl mx-auto flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <header className="flex items-center justify-between">
            <h1 className="flex items-center gap-2 text-2xl font-bold">
              <img src="/math-logo.svg" alt="logo" className="w-10 h-10" />
              클로바 튜터 계정 관리
            </h1>
          </header>
          <p className="text-muted-foreground text-sm ps-1">시스템에 등록된 계정을 조회하고 관리할 수 있습니다.</p>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <UserInput />
            <AddUserDialog />
          </div>

          <UserTable />
        </div>
      </div>
    </div>
  );
}
