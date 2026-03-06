/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { Navigation } from '../types/navigation';

/**
 * 브라우저의 Navigation API 지원 여부를 확인하는 타입 가드입니다.
 */
export function hasNavigationAPI(win: Window): win is Window & { navigation: Navigation } {
  return 'navigation' in win;
}
