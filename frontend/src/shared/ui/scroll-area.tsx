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

import * as ScrollAreaPrimitive from '@radix-ui/react-scroll-area';
import type React from 'react';

import { cn } from '@/shared/utils/utils';

export type ScrollAreaScrollDirection = 'vertical' | 'horizontal' | 'both';

export interface ScrollAreaProps extends React.ComponentProps<typeof ScrollAreaPrimitive.Root> {
  /** @default 'vertical' */
  scrollDirection?: ScrollAreaScrollDirection;
  componentProps?: {
    viewport?: React.ComponentProps<typeof ScrollAreaPrimitive.Viewport>;
    scrollbar?: React.ComponentProps<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>;
    scrollbarHorizontal?: React.ComponentProps<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>;
    corner?: React.ComponentProps<typeof ScrollAreaPrimitive.ScrollAreaCorner>;
  };
}

function ScrollArea({ className, children, scrollDirection = 'vertical', componentProps, ...props }: ScrollAreaProps) {
  const showVertical = scrollDirection === 'vertical' || scrollDirection === 'both';
  const showHorizontal = scrollDirection === 'horizontal' || scrollDirection === 'both';

  return (
    <ScrollAreaPrimitive.Root data-slot="scroll-area" className={cn('relative', className)} {...props}>
      <ScrollAreaPrimitive.Viewport
        data-slot="scroll-area-viewport"
        {...componentProps?.viewport}
        className={cn(
          'ring-ring/10 dark:ring-ring/20 dark:outline-ring/40 outline-ring/50 size-full rounded-[inherit] transition-[color,box-shadow] focus-visible:ring-4 focus-visible:outline-1',
          componentProps?.viewport?.className,
        )}
      >
        {children}
      </ScrollAreaPrimitive.Viewport>
      {showVertical && <ScrollBar orientation="vertical" {...componentProps?.scrollbar} />}
      {showHorizontal && <ScrollBar orientation="horizontal" {...componentProps?.scrollbarHorizontal} />}
      {showVertical && showHorizontal && <ScrollAreaPrimitive.Corner {...componentProps?.corner} />}
    </ScrollAreaPrimitive.Root>
  );
}

function ScrollBar({
  className,
  orientation = 'vertical',
  ...props
}: React.ComponentProps<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>) {
  return (
    <ScrollAreaPrimitive.ScrollAreaScrollbar
      data-slot="scroll-area-scrollbar"
      orientation={orientation}
      className={cn(
        'flex touch-none p-px transition-colors select-none',
        orientation === 'vertical' && 'h-full w-2.5 border-l border-l-transparent',
        orientation === 'horizontal' && 'h-2.5 flex-col border-t border-t-transparent',
        className,
      )}
      {...props}
    >
      <ScrollAreaPrimitive.ScrollAreaThumb
        data-slot="scroll-area-thumb"
        className="bg-border relative flex-1 rounded-full"
      />
    </ScrollAreaPrimitive.ScrollAreaScrollbar>
  );
}

export { ScrollArea, ScrollBar };
