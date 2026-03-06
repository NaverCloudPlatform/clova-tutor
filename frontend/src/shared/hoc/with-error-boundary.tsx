/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

'use client';

import type { ComponentType, ReactNode } from 'react';
import { ErrorBoundary } from '@/packages/error-boundary';

type ErrorBoundaryOptions = {
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
};

export function withErrorBoundary<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: ErrorBoundaryOptions = {},
) {
  const { fallback = null, onError } = options;

  function WithErrorBoundary(props: P) {
    return (
      <ErrorBoundary fallback={fallback} onError={onError}>
        <WrappedComponent {...props} />
      </ErrorBoundary>
    );
  }

  WithErrorBoundary.displayName = `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return WithErrorBoundary;
}
