/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export const DIFFICULTY_LEVEL = {
  LOW: {
    min: 1,
    max: 2,
  },
  MEDIUM: {
    min: 3,
    max: 4,
  },
  HIGH: {
    min: 5,
    max: 8,
  },
} as const;

export const DIFFICULTY_TEXT = {
  LOW: '하',
  MEDIUM: '중',
  HIGH: '상',
  UNKNOWN: '-',
} as const;
