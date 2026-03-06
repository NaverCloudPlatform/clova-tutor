/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ApiErrorBoundary as ApiErrorBoundaryComponent } from '@/packages/error-boundary';
import { Button } from './button';

type Props = {
  children: React.ReactNode;
} & React.ComponentProps<typeof ApiErrorBoundaryComponent>;

export function ApiErrorBoundary({ children, ...props }: Props) {
  return (
    <ApiErrorBoundaryComponent
      {...props}
      Button={({ children, ...props }) => (
        <Button variant="secondary" {...props}>
          {children}
        </Button>
      )}
    >
      {children}
    </ApiErrorBoundaryComponent>
  );
}
