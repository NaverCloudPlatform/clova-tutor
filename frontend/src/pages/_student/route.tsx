/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_student')({
  component: RouteComponent,
});

function RouteComponent() {
  return <Outlet />;
}
