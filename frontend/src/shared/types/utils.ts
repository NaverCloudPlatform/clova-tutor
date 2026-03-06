/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export type SetRequired<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;
