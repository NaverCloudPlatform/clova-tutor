/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_student/$subject/problems')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="@container px-4 pt-12 pb-8">
      <div className="max-w-5xl mx-auto">
        <Outlet />
      </div>
    </div>
  );
}
