/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, redirect } from '@tanstack/react-router';
import { queryClient } from '@/app/provider/tanstack-query';
import { usersQueries } from '@/entities/users/__generated__/api/queries';

export const Route = createFileRoute('/')({
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

      throw redirect({
        to: '/$subject',
        params: {
          subject: 'math',
        },
      });
    }

    throw redirect({
      to: '/login',
      search: {},
    });
  },
});

function RouteComponent() {
  return null;
}
