/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { IS_LOCAL } from '@/shared/constants/env';

const noop = () => {};

/**
 * 환경별로 console을 제어하는 로깅 유틸
 *
 * 각 로그 레벨별로 색상과 prefix가 자동으로 추가됩니다.
 */
export const log = {
  error: IS_LOCAL ? console.error.bind(console, '%c[ERROR]', 'color: red; font-weight: bold') : noop,
  warn: IS_LOCAL ? console.warn.bind(console, '%c[WARN]', 'color: orange; font-weight: bold') : noop,
  info: IS_LOCAL ? console.info.bind(console, '%c[INFO]', 'color: blue; font-weight: bold') : noop,
  debug: IS_LOCAL ? console.debug.bind(console, '%c[DEBUG]', 'color: green; font-weight: bold') : noop,
  log: IS_LOCAL ? console.log.bind(console) : noop,
};
