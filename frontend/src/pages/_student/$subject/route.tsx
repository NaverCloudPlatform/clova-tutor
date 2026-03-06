/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { z } from 'zod';
import { queryClient } from '@/app/provider/tanstack-query';
import { usersQueries } from '@/entities/users/__generated__/api/queries';
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/shared/ui/sidebar';
import { ChatSidebar } from '@/widgets/chat-sidebar/ui/chat-sidebar';

const searchSchema = z.object({});

export const Route = createFileRoute('/_student/$subject')({
  component: RouteComponent,
  beforeLoad: async () => {
    const userId = localStorage.getItem('userId');

    if (userId) {
      const user = await queryClient.ensureQueryData({
        ...usersQueries.getUsersByUserId({ userId }),
        retry: false,
      });

      if (!user) {
        throw new Error('User not found');
      }

      return;
    }

    throw redirect({
      to: '/login',
      search: {},
    });
  },
  validateSearch: zodValidator(searchSchema),
});

function RouteComponent() {
  return (
    <SidebarProvider>
      <ChatSidebar />
      <SidebarInset className="@container/sidebar-inset">
        <SidebarTrigger className="absolute top-2 left-2 md:hidden z-10" />
        <Outlet />
      </SidebarInset>
    </SidebarProvider>
  );
}
