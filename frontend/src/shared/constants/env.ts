/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export const IS_LOCAL = import.meta.env.MODE === 'development';
export const IS_PROD = !IS_LOCAL;

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
