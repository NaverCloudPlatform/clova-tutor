/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

// Components

export * from 'react-error-boundary';
export { ErrorBoundary as BaseErrorBoundary } from 'react-error-boundary';
export {
  ApiErrorBoundary,
  type TApiErrorBoundaryProps,
} from './components/api-error-boundary';
export {
  ErrorBoundary,
  type TErrorBoundaryProps,
} from './components/error-boundary';
// Constants (for customization)
export {
  HTTP_ERROR_ACTION_CONFIG,
  HTTP_ERROR_CONFIG,
} from './constants/http-error-message';
// Types
export type {
  TErrorConfigElementType as ErrorConfigElementType,
  TPartialErrorConfig as PartialErrorConfig,
} from './types/api-error';
// Utils
export { getErrorConfig } from './utils/api-error';
