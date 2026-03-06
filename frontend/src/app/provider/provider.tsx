/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { PropsWithChildren } from 'react';
import { TanstackQueryProvider } from '@/app/provider/tanstack-query.tsx';
import { ThemeProvider } from '@/app/provider/theme-provider.tsx';
import { MarkdownClipboardWrapper } from '@/packages/markdown/ui/markdown-clipboard-wrapper';

export function Provider({ children }: PropsWithChildren) {
  return (
    <ThemeProvider>
      <TanstackQueryProvider>
        <MarkdownClipboardWrapper>{children}</MarkdownClipboardWrapper>
      </TanstackQueryProvider>
    </ThemeProvider>
  );
}
