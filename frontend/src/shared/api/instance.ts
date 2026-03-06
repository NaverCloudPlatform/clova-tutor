/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { KyInstance } from 'ky';
import ky from 'ky';
import { API_BASE_URL } from '@/shared/constants/env';

export const kyInstance: KyInstance = ky.create({
  prefixUrl: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
  hooks: {
    beforeRequest: [
      (request) => {
        const userId = localStorage.getItem('userId');

        const url = new URL(request.url);

        if (url.pathname.startsWith('/api/v1/users')) return request;

        if (!userId) {
          window.location.href = '/login';

          return new Response(JSON.stringify({ error: 'Unauthorized' }), {
            status: 401,
            headers: {
              'Content-Type': 'application/json',
            },
          });
        }

        request.headers.set('X-User-Id', userId);
        return request;
      },
    ],
    afterResponse: [
      async (_, __, response) => {
        const contentType = response.headers.get('Content-Type');
        if (contentType?.includes('text/event-stream')) {
          return response;
        }

        if (response.status === 403) {
          localStorage.removeItem('userId');
          setTimeout(() => {
            window.location.href = '/login';
          }, 0);
          return;
        }

        if (response.status === 401 || response.status === 400) {
          const clonedResponse = response.clone();
          const data = await clonedResponse.json();

          if (data?.detail?.kind === 'HeaderTypeNotMatchException') {
            localStorage.removeItem('userId');
            setTimeout(() => {
              window.location.href = '/login';
            }, 0);
            return;
          }
        }

        return response;
      },
    ],
  },
});
