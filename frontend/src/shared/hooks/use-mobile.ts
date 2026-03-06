/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

/**
 * This file is based on code from shadcn/ui (https://ui.shadcn.com).
 * Licensed under the MIT License.
 * See: https://github.com/shadcn-ui/ui/blob/main/LICENSE.md
 */

import * as React from 'react';

const MOBILE_BREAKPOINT = 768;

export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined);

  React.useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`);
    const onChange = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT);
    };
    mql.addEventListener('change', onChange);
    setIsMobile(window.innerWidth < MOBILE_BREAKPOINT);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  return !!isMobile;
}
