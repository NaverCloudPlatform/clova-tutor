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

import * as SeparatorPrimitive from '@radix-ui/react-separator';

import { cn } from '@/shared/utils/utils';

function Separator({
  className,
  orientation = 'horizontal',
  decorative = true,
  ...props
}: React.ComponentProps<typeof SeparatorPrimitive.Root>) {
  return (
    <SeparatorPrimitive.Root
      data-slot="separator-root"
      decorative={decorative}
      orientation={orientation}
      className={cn(
        'bg-border shrink-0 data-[orientation=horizontal]:h-px data-[orientation=horizontal]:w-full data-[orientation=vertical]:h-full data-[orientation=vertical]:w-px',
        className,
      )}
      {...props}
    />
  );
}

export { Separator };
