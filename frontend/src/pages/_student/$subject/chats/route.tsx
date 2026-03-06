/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, Outlet } from '@tanstack/react-router';
import { ModelChangeDropdown } from '@/widgets/chat-onboarding/ui/model-change-dropdown';
import { MathVirtualKeyboardContainerLayout } from './-components/math-virtual-keyboard-container-layout';

export const Route = createFileRoute('/_student/$subject/chats')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="h-svh sm:h-[calc(100svh-(--spacing(4)))]">
      <MathVirtualKeyboardContainerLayout className="flex flex-col justify-between w-full @container">
        <header className="h-12 min-h-12 ps-11 md:px-3 flex items-center justify-between">
          <ModelChangeDropdown />
        </header>

        <Outlet />
      </MathVirtualKeyboardContainerLayout>
    </div>
  );
}
