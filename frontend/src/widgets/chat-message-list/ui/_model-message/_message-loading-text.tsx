/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { cn } from '@/shared/utils/utils';
import { useRotatingLoadingMessage } from '../../hooks/use-rotating-loading-message';

type MessageLoadingTextProps = {
  className?: string;
};

export function MessageLoadingText({ className }: MessageLoadingTextProps) {
  const loadingMessage = useRotatingLoadingMessage();

  return (
    <>
      <div className="h-6" />
      <div className={cn('group-last:block hidden animate-pulse pt-1', className)}>
        <span className="ai-text font-semibold text-base">{loadingMessage}</span>
      </div>
    </>
  );
}
