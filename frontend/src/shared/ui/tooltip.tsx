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

'use client';

import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import { createContext, useContext, useRef, useState } from 'react';

import { cn } from '@/shared/utils/utils';

const LONG_PRESS_DURATION_MS = 700;

type TooltipContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
  isTouchDeviceRef: React.RefObject<boolean>;
};

const TooltipContext = createContext<TooltipContextValue | null>(null);

function TooltipProvider({ delayDuration = 0, ...props }: React.ComponentProps<typeof TooltipPrimitive.Provider>) {
  return <TooltipPrimitive.Provider data-slot="tooltip-provider" delayDuration={delayDuration} {...props} />;
}

function Tooltip({ open: controlledOpen, onOpenChange, ...props }: React.ComponentProps<typeof TooltipPrimitive.Root>) {
  const [internalOpen, setInternalOpen] = useState(false);
  const isTouchDeviceRef = useRef(false);
  const open = controlledOpen ?? internalOpen;

  const setOpen = (nextOpen: boolean) => {
    setInternalOpen(nextOpen);
    onOpenChange?.(nextOpen);
  };

  const handleOpenChange = (nextOpen: boolean) => {
    // 터치 디바이스에서는 Radix의 자동 열림(focus/hover)을 차단, long-press로만 열림
    if (nextOpen && isTouchDeviceRef.current) {
      return;
    }
    setOpen(nextOpen);
  };

  return (
    <TooltipContext.Provider value={{ open, setOpen, isTouchDeviceRef }}>
      <TooltipProvider>
        <TooltipPrimitive.Root data-slot="tooltip" open={open} onOpenChange={handleOpenChange} {...props} />
      </TooltipProvider>
    </TooltipContext.Provider>
  );
}

function TooltipTrigger({ ...props }: React.ComponentProps<typeof TooltipPrimitive.Trigger>) {
  const context = useContext(TooltipContext);
  const longPressTimerRef = useRef<ReturnType<typeof setTimeout>>(null);

  return (
    <TooltipPrimitive.Trigger
      data-slot="tooltip-trigger"
      onTouchStart={(e) => {
        // 한 번이라도 터치하면 터치 디바이스로 간주 (세션 동안 유지)
        if (context?.isTouchDeviceRef) {
          context.isTouchDeviceRef.current = true;
        }

        longPressTimerRef.current = setTimeout(() => {
          context?.setOpen(true);
        }, LONG_PRESS_DURATION_MS);

        props.onTouchStart?.(e);
      }}
      onTouchEnd={(e) => {
        if (longPressTimerRef.current) clearTimeout(longPressTimerRef.current);
        props.onTouchEnd?.(e);
      }}
      onContextMenu={(e) => {
        e.preventDefault();
        props.onContextMenu?.(e);
      }}
      {...props}
    />
  );
}

function TooltipContent({
  className,
  sideOffset = 4,
  children,
  arrow = true,
  ...props
}: React.ComponentProps<typeof TooltipPrimitive.Content> & { arrow?: boolean }) {
  return (
    <TooltipPrimitive.Portal>
      <TooltipPrimitive.Content
        data-slot="tooltip-content"
        sideOffset={sideOffset}
        className={cn(
          'bg-primary text-primary-foreground animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 max-w-sm rounded-md px-3 py-1.5 text-xs',
          className,
        )}
        {...props}
      >
        {children}
        {arrow && (
          <TooltipPrimitive.Arrow className="bg-primary fill-primary z-50 size-2.5 translate-y-[calc(-50%_-_2px)] rotate-45 rounded-[2px]" />
        )}
      </TooltipPrimitive.Content>
    </TooltipPrimitive.Portal>
  );
}

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider };
