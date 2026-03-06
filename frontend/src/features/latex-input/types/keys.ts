/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export type Key = {
  label: string | React.ReactElement;
  value: string;
  action?: 'keystroke' | 'latex' | 'text';
  className?: string;
  tooltip?: string;
};
