/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { MutationCache, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { HTTPError } from 'ky';
import type { PropsWithChildren } from 'react';
import { ZodValidationError } from '@/shared/api/__generated__/utils';
import { globalMutationEffects, isGlobalMutationEffectKey } from '@/shared/api/global-mutation-effects';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 0,
      retry: (failureCount, error) => {
        if (error instanceof ZodValidationError) {
          return false;
        }

        if (error instanceof HTTPError) {
          if (error.response.status === 404) return false;
        }

        return failureCount < 2;
      },
    },
  },
  mutationCache: new MutationCache({
    onSuccess: async (_data, _variables, _context, mutation) => {
      const disableGlobalInvalidation = mutation.options.meta?.disableGlobalInvalidation;
      const mutationFnName = mutation.options.meta?.mutationFnName;
      const mutationKey = mutation.options.mutationKey;

      if (disableGlobalInvalidation) {
        // 전역 invalidate를 비활성화 한 경우 종료 (ProblemBookmarkToggleButton 처럼 특수한 경우에 사용함)
        return;
      }

      if (isGlobalMutationEffectKey(mutationFnName)) {
        // invalidate handlers에 등록된 동작이 있다면, 해당 동작을 수행하고 entity 단위 invalidate를 수행하지 않음
        const invalidate = globalMutationEffects(queryClient)[mutationFnName]?.onSuccess.invalidate;

        if (invalidate) {
          invalidate(_data as never, _variables as never, _context as never, mutation as never);
          return;
        }
      }

      if (!mutationKey) return;

      // entity 단위 invalidate
      await queryClient.invalidateQueries({
        queryKey: [mutationKey?.at(0)],
        exact: false,
      });

      const cache = queryClient.getMutationCache();
      const sameKeyMutations = cache
        .getAll()
        .filter(
          (m) => JSON.stringify(m.options.mutationKey) === JSON.stringify(mutationKey) && m.state.status === 'success',
        );

      sameKeyMutations
        .filter((m) => m !== mutation)
        .forEach((m) => {
          cache.remove(m);
        });
    },
  }),
});

export const TanstackQueryProvider = ({ children }: PropsWithChildren) => {
  return (
    <QueryClientProvider client={queryClient}>
      <ReactQueryDevtools initialIsOpen={false} />
      {children}
    </QueryClientProvider>
  );
};
