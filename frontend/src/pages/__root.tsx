/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createRootRoute, HeadContent, Outlet, retainSearchParams } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { z } from 'zod';
import { Provider } from '@/app/provider';
import { ConfettiContainer } from '@/shared/ui/confetti-container';
import { GlobalErrorBoundary } from '@/shared/ui/global-error-boundary';
import { Toaster } from '@/shared/ui/sonner';

export const Route = createRootRoute({
  validateSearch: zodValidator(
    z.object({
      dev: z.boolean().optional(),
      scenario: z.string().optional(),
    }),
  ),
  search: {
    middlewares: [retainSearchParams(['dev', 'scenario'])],
  },
  component: () => (
    <>
      <HeadContent />
      <GlobalErrorBoundary>
        <Provider>
          <Outlet />
          <Toaster />
          <ConfettiContainer />

        </Provider>
      </GlobalErrorBoundary>
    </>
  ),
});
