/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useEffect, useState } from 'react';
import { log } from '@/shared/core/log';
import { useIsMobile } from '@/shared/hooks/use-mobile';
import { useSidebar } from '@/shared/ui/sidebar';
import { cn } from '@/shared/utils/utils';

type Props = {
  className?: string;
  children: React.ReactNode;
};

export function MathVirtualKeyboardContainerLayout({ className, children }: Props) {
  const isMobile = useIsMobile();
  const { open } = useSidebar();
  const [mathVirtualKeyboardHeight, setMathVirtualKeyboardHeight] = useState(0);
  const [isMathVirtualKeyboardVisible, setIsMathVirtualKeyboardVisible] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.mathVirtualKeyboard) {
      return;
    }

    // requestAnimationFrame으로 DOM이 완전히 렌더링된 후 컨테이너 설정
    const rafId = requestAnimationFrame(() => {
      const container = document.getElementById('math-virtual-keyboard-container');

      if (!container) {
        log.warn('math-virtual-keyboard-container element not found');
        return;
      }

      // 다른 채팅방 이동 후 돌아왔을 때도 새로운 컨테이너로 재설정
      window.mathVirtualKeyboard.container = container;
    });

    // 가상키보드 가시성 변화 감지
    const handleVisibilityChange = () => {
      setIsMathVirtualKeyboardVisible(window.mathVirtualKeyboard.visible);

      setMathVirtualKeyboardHeight(window.mathVirtualKeyboard.boundingRect.height);
    };

    const handleGeometryChange = () => {
      if (window.mathVirtualKeyboard.visible) {
        setMathVirtualKeyboardHeight(window.mathVirtualKeyboard.boundingRect.height);
      }
    };

    // 가시성 변화 이벤트 리스너 등록
    window.mathVirtualKeyboard.addEventListener('virtual-keyboard-toggle', handleVisibilityChange);

    window.mathVirtualKeyboard.addEventListener('geometrychange', handleGeometryChange);

    return () => {
      cancelAnimationFrame(rafId);
      window.mathVirtualKeyboard.removeEventListener('virtual-keyboard-toggle', handleVisibilityChange);
      window.mathVirtualKeyboard.removeEventListener('geometrychange', handleGeometryChange);

      // 언마운트 시 가상 키보드 컨테이너를 기본값(document.body)으로 복원
      window.mathVirtualKeyboard.container = document.body;
    };
  }, []);

  return (
    <>
      <div
        className={cn(className)}
        style={{
          height: isMathVirtualKeyboardVisible ? `calc(100% - ${mathVirtualKeyboardHeight}px)` : '100%',
        }}
      >
        {children}
      </div>

      <div className="relative">
        <div
          id="math-virtual-keyboard-container"
          className={cn('absolute top-0 w-screen', isMobile ? '' : open ? '-left-[var(--sidebar-width)]' : 'left-0')}
          style={{
            height: mathVirtualKeyboardHeight,
          }}
        />
      </div>
    </>
  );
}
