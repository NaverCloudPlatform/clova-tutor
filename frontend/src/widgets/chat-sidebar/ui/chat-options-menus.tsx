/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { CircleUserRoundIcon, LogOutIcon } from 'lucide-react';
import { Suspense } from 'react';
import { UserProfile, UserProfileSkeleton } from '@/entities/users/ui/user-profile';
import { ErrorBoundary } from '@/packages/error-boundary';
import { LOCAL_STORAGE_KEY } from '@/shared/constants/storage-key';
import { Button } from '@/shared/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu';
import { ThemeChangeDropdown } from './theme-change-dropdown';

export function ChatOptionsMenus() {
  const handleLogout = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY.USER_ID);
    window.location.replace('/login');
  };

  return (
    <div className="flex items-center gap-1">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" aria-label="유저 정보 메뉴">
            <CircleUserRoundIcon className="size-6" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56 p-3">
          <ErrorBoundary fallbackRender={() => <UserProfileSkeleton />}>
            <Suspense fallback={<UserProfileSkeleton />}>
              <UserProfile />
            </Suspense>
          </ErrorBoundary>

          <DropdownMenuSeparator className="mx-2" />

          <ThemeChangeDropdown />

          <DropdownMenuSeparator className="mx-2" />

          <DropdownMenuItem onClick={handleLogout}>
            <LogOutIcon />
            로그아웃
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
