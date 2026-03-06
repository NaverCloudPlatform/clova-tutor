/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ClipboardEventHandler, PropsWithChildren } from 'react';
import { useKatexSelection } from '../hooks/use-katex-selection';
import { fragmentToMarkdown } from '../lib/dom-utils';

export function MarkdownClipboardWrapper({ children }: PropsWithChildren) {
  useKatexSelection();

  const handleCopy: ClipboardEventHandler<HTMLDivElement> = (e) => {
    const target = e.target as HTMLElement;
    if (target.closest('input, textarea, [contenteditable="true"]')) {
      return;
    }

    e.preventDefault();
    e.clipboardData?.setData('text/plain', fragmentToMarkdown());
  };

  return <div onCopy={handleCopy}>{children}</div>;
}
