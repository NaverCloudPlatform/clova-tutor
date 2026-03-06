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

import { useTheme } from '@/app/provider/theme-provider';
import { Toaster as Sonner, type ToasterProps } from 'sonner';

const Toaster = ({ ...props }: ToasterProps) => {
  const { resolvedTheme } = useTheme();

  return (
    <>
      <style>
        {`[data-sonner-toaster] {
          z-index: 50;
        }
        [data-sonner-toast] [data-title],
        [data-sonner-toast] [data-description] {
          white-space: pre-line;
          word-break: keep-all;
          overflow-wrap: anywhere;
        }`}
      </style>
      <Sonner
        theme={resolvedTheme}
        className="toaster group"
        style={
          {
            '--normal-bg': 'var(--popover)',
            '--normal-text': 'var(--popover-foreground)',
            '--normal-border': 'var(--border)',
          } as React.CSSProperties
        }
        position="top-right"
        offset={{ top: 8, right: 8 }}
        {...props}
      />
    </>
  );
};

export { Toaster };
