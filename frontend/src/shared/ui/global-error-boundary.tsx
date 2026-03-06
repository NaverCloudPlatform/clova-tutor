/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

'use client';

import { ErrorBoundary } from '@/packages/error-boundary';
import { Button } from '@/shared/ui/button';

type Props = {
  children: React.ReactNode;
};

export function GlobalErrorBoundary({ children }: Props) {
  return (
    <ErrorBoundary
      fallback={
        <div className="flex flex-col items-center justify-center min-h-screen p-4 gap-y-2 bg-background">
          <p className="text-sm text-muted-foreground">오류가 발생했습니다.</p>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            새로고침
          </Button>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}
