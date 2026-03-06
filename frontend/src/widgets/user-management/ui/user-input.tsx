/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useRouter, useSearch } from '@tanstack/react-router';
import { debounce } from 'es-toolkit';
import { useCallback, useMemo } from 'react';
import { Input } from '@/shared/ui/input';

export function UserInput() {
  const router = useRouter();
  const search = useSearch({ from: '/login/' });

  const updateUrl = useCallback(
    (value: string) => {
      router.navigate({
        to: '.',
        search: {
          ...search,
          username: value.trim() || undefined,
        },
        replace: true,
      });
    },
    [router, search],
  );

  const debouncedUpdateUrl = useMemo(() => debounce(updateUrl, 300), [updateUrl]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      debouncedUpdateUrl(e.target.value);
    },
    [debouncedUpdateUrl],
  );

  return (
    <Input
      type="text"
      className="bg-background"
      placeholder="이름을 입력하세요"
      defaultValue={search.username || ''}
      onChange={handleChange}
    />
  );
}
