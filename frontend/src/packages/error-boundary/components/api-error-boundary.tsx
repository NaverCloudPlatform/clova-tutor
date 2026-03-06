/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { QueryErrorResetBoundary } from '@tanstack/react-query';
import { useRouter } from '@tanstack/react-router';
import type { HTTPError } from 'ky';
import type React from 'react';
import { ErrorBoundary, type ErrorBoundaryProps, type FallbackProps } from 'react-error-boundary';
import { match, P } from 'ts-pattern';
import { Button } from '@/shared/ui/button';
import type { TPartialErrorConfig } from '../types/api-error';
import { getErrorConfig, isApiError } from '../utils/api-error';

export type TIgnoreErrorType = string | number | ((error: HTTPError) => boolean);

const DefaultButton = (props: React.ComponentProps<'button'>) => (
  <Button variant="secondary" {...props}>
    {props.children}
  </Button>
);

export type TApiErrorBoundaryProps = {
  children: React.ReactNode;
  FallbackContainer?: React.ComponentType<{ children: React.ReactNode }>;
  Button?: React.ComponentType<React.ComponentProps<'button'>>;
  overrideConfig?: TPartialErrorConfig;
  resetKeys?: ErrorBoundaryProps['resetKeys'];
  ignoreError?: TIgnoreErrorType[];
};

export function ApiErrorBoundary({
  children,
  FallbackContainer = ({ children }) => <div className="flex-1 flex h-full">{children}</div>,
  Button = DefaultButton,
  overrideConfig,
  resetKeys,
  ignoreError = [],
}: TApiErrorBoundaryProps) {
  const handleError: ErrorBoundaryProps['onError'] = (error, info) => {
    if (!isApiError(error)) {
      throw error;
    }

    const shouldIgnore = ignoreError.some((ignore) =>
      match(ignore)
        .with(P.string, (ignoreStatusText) => {
          const statusText = error.response.statusText;
          return statusText.match(ignoreStatusText);
        })
        .with(P.number, (ignoreStatus) => {
          const status = error.response.status;
          return status === ignoreStatus;
        })
        .with(P.instanceOf(Function), (ignoreErrorFunction) => ignoreErrorFunction(error))
        .otherwise(() => false),
    );

    if (shouldIgnore) {
      throw error;
    }

    const targetErrorConfig = getErrorConfig(error, overrideConfig);
    if (targetErrorConfig && 'onError' in targetErrorConfig && targetErrorConfig.onError) {
      const status = error.response.status;
      targetErrorConfig.onError(error, info, status);
    }
  };

  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          fallbackRender={({ error, resetErrorBoundary }) =>
            isApiError(error) ? (
              <FallbackContainer>
                <ApiErrorFallback
                  error={error}
                  resetErrorBoundary={resetErrorBoundary}
                  overrideConfig={overrideConfig}
                  Button={Button}
                />
              </FallbackContainer>
            ) : null
          }
          onError={handleError}
          onReset={reset}
          resetKeys={resetKeys}
        >
          {children}
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}

type ApiErrorFallbackProps = {
  error: HTTPError;
  resetErrorBoundary: FallbackProps['resetErrorBoundary'];
  overrideConfig?: TPartialErrorConfig;
  Button: React.ComponentType<React.ComponentProps<'button'>>;
};

function ApiErrorFallback({ error, resetErrorBoundary, overrideConfig, Button }: ApiErrorFallbackProps) {
  const router = useRouter();
  const targetErrorConfig = getErrorConfig(error, overrideConfig);

  const handleActionButtonClick = () => {
    if (!targetErrorConfig || !('action' in targetErrorConfig) || !targetErrorConfig.action) {
      return;
    }

    match(targetErrorConfig.action.type)
      .with('go-back', () => {
        router.history.back();
      })
      .with('go-login', () => {
        router.navigate({ to: '/login', replace: true });
      })
      .with('retry', () => {
        resetErrorBoundary();
      })
      .with('go-root', () => {
        router.navigate({ to: '/', replace: true });
      });
  };

  return match(targetErrorConfig)
    .with({ type: 'default', action: { message: P._ }, message: P._ }, ({ action, message }) => {
      return (
        <div className="flex flex-1 flex-col items-center justify-center p-4 gap-y-2">
          <p className="text-sm text-muted-foreground">{message}</p>
          <Button onClick={handleActionButtonClick}>{action.message}</Button>
        </div>
      );
    })
    .with({ type: 'custom' }, (config) => {
      const { fallback } = config;

      if (typeof fallback === 'function') {
        return fallback(error, resetErrorBoundary);
      }

      return fallback;
    })
    .otherwise(() => null);
}
