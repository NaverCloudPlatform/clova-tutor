/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useCallback, useRef } from 'react';

type TParams = {
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
  observerInit?: Omit<IntersectionObserverInit, 'root'>;
};

export function useInfiniteScroll({ hasNextPage, isFetchingNextPage, fetchNextPage, observerInit }: TParams) {
  const observerRootRef = useRef<HTMLDivElement | null>(null);
  const observer = useRef<IntersectionObserver | null>(null);

  const lastElementRef = useCallback(
    (node: HTMLDivElement | HTMLTableRowElement | null) => {
      if (isFetchingNextPage) return;
      if (observer.current) {
        return;
      }

      observer.current = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
            fetchNextPage();
          }
        },
        {
          threshold: 0,
          rootMargin: '10px 0px',
          ...observerInit,
          root: observerRootRef.current,
        },
      );

      if (node) observer.current.observe(node);
    },
    [isFetchingNextPage, hasNextPage, fetchNextPage, observerInit],
  );

  return {
    observerRootRef,
    lastElementRef,
  };
}
