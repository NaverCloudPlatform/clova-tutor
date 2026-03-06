/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useEffect } from 'react';
import type { NavigationEvent } from '@/shared/types/navigation';
import { hasNavigationAPI } from '../guard/window';

type useWindowNavigationInterceptParams = {
  /** 가로챌 대상인지 판단하는 조건 */
  shouldIntercept: (url: URL) => boolean;
  /** 가로챘을 때 실행할 핸들러 */
  onIntercept?: (url: URL) => void;
}

/**
 * 브라우저의 Navigation API를 활용하여 페이지 이탈을 가로채고 제어하는 훅입니다.
 * * @description
 * 크로미움 기반 브라우저에서 라우터의 'Loader' 기능을 통해 이동을 막을 때,
 * 실제 경로는 유지되지만 `document.title`만 목적지의 제목으로 먼저 변경되는 현상을 해결합니다.
 * * @note 
 * - Navigation API는 현재 Chromium 기반 브라우저(Chrome, Edge 등)에서만 지원됩니다.
 * - `history.traverse`(뒤로 가기/앞으로 가기) 시점에 작동하며, 조건부로 이동을 취소하고 현재 상태를 유지합니다.
 * * @param params.shouldIntercept - 내비게이션을 차단할지 여부를 판단하는 조건 함수
 * @param params.onIntercept - 내비게이션이 가로채졌을 때 실행할 사이드 이펙트 핸들러
 */
export function useWindowNavigationIntercept({
  shouldIntercept,
  onIntercept,
}: useWindowNavigationInterceptParams) {
  useEffect(() => {
    if (!hasNavigationAPI(window)) return;

    const nav = window.navigation;

    const handleNavigate = (event: NavigationEvent) => {
      if (event.navigationType !== 'traverse' || !event.canIntercept) return;

      const destinationUrl = new URL(event.destination.url);

      if (shouldIntercept(destinationUrl)) {
        event.intercept({
          handler: async () => {
            onIntercept?.(destinationUrl);
            
            await nav.navigate(window.location.href, { history: 'replace' });
          },
        });
      }
    };

    nav.addEventListener('navigate', handleNavigate);
    return () => nav.removeEventListener('navigate', handleNavigate);
  }, [shouldIntercept, onIntercept]);
}