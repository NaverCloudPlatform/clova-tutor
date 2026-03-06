/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { type ComponentType, type ReactNode, Suspense } from 'react';

type WithSuspenseOptions = {
  fallback?: ReactNode;
};

/**
 * Suspense를 HoC로 적용하는 함수
 *
 * @param Component - Suspense로 감쌀 컴포넌트
 * @param options - Suspense 옵션 (fallback)
 * @returns Suspense로 감싸진 컴포넌트
 *
 * @example
 * ```tsx
 * const MyComponentWithSuspense = withSuspense(MyComponent);
 * ```
 *
 * @example
 * ```tsx
 * const MyComponentWithSuspense = withSuspense(MyComponent, {
 *   fallback: <Skeleton />
 * });
 * ```
 */
export function withSuspense<P extends object>(
  Component: ComponentType<P>,
  options?: WithSuspenseOptions,
): ComponentType<P> {
  const fallback = options?.fallback ?? null;

  const WrappedComponent = (props: P) => {
    return (
      <Suspense fallback={fallback}>
        <Component {...props} />
      </Suspense>
    );
  };

  WrappedComponent.displayName = `withSuspense(${Component.displayName || Component.name || 'Component'})`;

  return WrappedComponent;
}
