/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { Label } from '@/shared/ui/label';
import { usersQueries } from '../__generated__/api/queries';
import { gradeToName } from '../utils/user-grade';

export function UserProfile() {
  const { data: user } = useSuspenseQuery({
    ...usersQueries.getUsersByUserId({
      userId: localStorage.getItem('userId') ?? '',
    }),
  });

  return (
    <div className="p-2 space-y-1">
      <div className="flex items-center gap-4">
        <Label className="font-semibold shrink-0">이름</Label>
        <p className="text-sm wrap-anywhere">{user?.name}</p>
      </div>

      <div className="flex items-center gap-4">
        <Label className="font-semibold">학년</Label>
        <p className="text-sm">{gradeToName(user?.grade)}</p>
      </div>
    </div>
  );
}

export function UserProfileSkeleton() {
  return (
    <div className="p-2 space-y-1">
      <div className="flex items-center gap-4">
        <Label className="font-semibold">이름</Label>
        <p className="text-sm">-</p>
      </div>
      <div className="flex items-center gap-4">
        <Label className="font-semibold">학년</Label>
        <p className="text-sm">-</p>
      </div>
    </div>
  );
}
