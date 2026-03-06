/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { cn } from '@/shared/utils/utils';

export function Table({ className, ...props }: React.ComponentProps<'table'>) {
  return <table {...props} className={cn('w-full my-[1.2em]', className)} />;
}

export function TableHeader({ className, ...props }: React.ComponentProps<'thead'>) {
  return <thead {...props} className={cn('bg-muted', className)} />;
}

export function TableBody({ className, ...props }: React.ComponentProps<'tbody'>) {
  return <tbody {...props} className={cn('[&_tr:last-child]:border-0', className)} />;
}

export function TableRow({ className, ...props }: React.ComponentProps<'tr'>) {
  return <tr {...props} className={cn('m-0 p-0 even:bg-muted', className)} />;
}

export function TableCell({ className, ...props }: React.ComponentProps<'td'>) {
  return (
    <td
      {...props}
      className={cn(
        'border-t px-[1em] py-[0.5em] text-left [&[align=center]]:text-center [&[align=right]]:text-right',
        className,
      )}
    />
  );
}

export function TableHead({ className, ...props }: React.ComponentProps<'th'>) {
  return (
    <th
      {...props}
      className={cn(
        'border-b px-[1em] py-[0.5em] text-left font-semibold [&[align=center]]:text-center [&[align=right]]:text-right',
        className,
      )}
    />
  );
}
