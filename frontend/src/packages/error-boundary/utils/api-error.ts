/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { HTTPError } from 'ky';
import { HTTP_ERROR_CONFIG } from '../constants/http-error-message';
import type { TPartialErrorConfig } from '../types/api-error';

export const getErrorConfig = (error: HTTPError, overrideConfig?: TPartialErrorConfig) => {
  const statusCode = Object.keys(HTTP_ERROR_CONFIG).includes(error.response?.status?.toString() ?? '')
    ? error.response?.status
    : 500;

  const defaultConfig = HTTP_ERROR_CONFIG[statusCode as keyof typeof HTTP_ERROR_CONFIG];
  const override = overrideConfig?.[statusCode as keyof typeof HTTP_ERROR_CONFIG];

  return override ?? defaultConfig;
};

export const isKyError = (err: unknown): err is HTTPError => {
  return err instanceof HTTPError;
};

export const isApiError = (err: unknown) => {
  return isKyError(err);
};
