/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useEffect, useRef, useState } from 'react';

export function useIsTextClamped<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [isClamped, setIsClamped] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const checkClamped = () => {
      // 소수점 반올림 차이로 인한 오차 허용
      const TOLERANCE = 2;

      setIsClamped(element.scrollHeight > element.clientHeight + TOLERANCE);
    };

    const resizeObserver = new ResizeObserver(() => {
      requestAnimationFrame(checkClamped);
    });

    resizeObserver.observe(element);
    checkClamped();

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  return {
    ref,
    isClamped,
  };
}
