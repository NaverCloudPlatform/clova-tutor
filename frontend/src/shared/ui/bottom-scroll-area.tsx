/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ArrowDown } from 'lucide-react';
import type { PropsWithChildren, RefObject } from 'react';
import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { ScrollArea, type ScrollAreaProps } from '@/shared/ui/scroll-area';
import { cn } from '../utils/utils';
import { Button } from './button';

type BottomScrollContextValue = {
  scrollAreaRef: RefObject<HTMLDivElement | null>;
  scrollToBottom: ({ smooth }: { smooth?: boolean }) => void;
};

const BottomScrollContext = createContext<BottomScrollContextValue | null>(null);

export function useBottomScrollContext() {
  const context = useContext(BottomScrollContext);
  if (!context) {
    throw new Error('useBottomScrollContext must be used within BottomScrollArea');
  }
  return context;
}

type BottomScrollAreaProps = Omit<ScrollAreaProps, 'className'> & {
  classNames?: {
    base?: string;
    button?: string;
  };
};

export function BottomScrollArea({ children }: PropsWithChildren<BottomScrollAreaProps>) {
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = useCallback(({ smooth = true }: { smooth?: boolean } = {}) => {
    const element = scrollAreaRef.current;
    if (!element) return;

    if (smooth) {
      element.scrollTo({
        top: element.scrollHeight,
        behavior: 'smooth',
      });
    } else {
      // Safari에서 scrollTo({ behavior: 'instant' })가 이상하게 동작할 수 있어서
      // smooth가 아닐 때는 직접 scrollTop 할당
      element.scrollTop = element.scrollHeight;
    }
  }, []);

  return (
    <BottomScrollContext.Provider value={{ scrollAreaRef, scrollToBottom }}>{children}</BottomScrollContext.Provider>
  );
}

export function BottomScrollAreaContent({ children, classNames, ...props }: BottomScrollAreaProps) {
  const { scrollAreaRef, scrollToBottom } = useBottomScrollContext();
  const [showScrollButton, setShowScrollButton] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const lastScrollTopRef = useRef<number>(0);

  const checkScroll = useCallback(() => {
    if (scrollAreaRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollAreaRef.current;
      const isNotAtBottom = scrollHeight - scrollTop - clientHeight > 1;

      setShowScrollButton(isNotAtBottom);
    }
  }, [scrollAreaRef]);

  // Safari 스크롤 점프 방지: 갑작스러운 스크롤 변화 감지 및 복원
  useEffect(() => {
    const viewport = scrollAreaRef.current;
    if (!viewport) return;

    // Safari 감지
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (!isSafari) return;

    let isUserScrolling = false;
    let scrollTimeout: ReturnType<typeof setTimeout>;

    const handleScroll = () => {
      const currentScrollTop = viewport.scrollTop;
      const diff = currentScrollTop - lastScrollTopRef.current;

      // 사용자가 직접 스크롤 중이면 정상적인 스크롤로 간주
      if (isUserScrolling) {
        lastScrollTopRef.current = currentScrollTop;
        return;
      }

      // 100px 이상 갑자기 위로 이동하면 (Safari의 비정상 스크롤)
      // 이전 위치로 복원
      if (diff < -100) {
        console.log('[Safari scroll fix] Restoring scroll from', currentScrollTop, 'to', lastScrollTopRef.current);
        viewport.scrollTop = lastScrollTopRef.current;
        return;
      }

      lastScrollTopRef.current = currentScrollTop;
    };

    const handleTouchStart = () => {
      isUserScrolling = true;
    };

    const handleTouchEnd = () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        isUserScrolling = false;
      }, 100);
    };

    const handleWheel = () => {
      isUserScrolling = true;
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        isUserScrolling = false;
      }, 100);
    };

    viewport.addEventListener('scroll', handleScroll, true);
    viewport.addEventListener('touchstart', handleTouchStart, { passive: true });
    viewport.addEventListener('touchend', handleTouchEnd, { passive: true });
    viewport.addEventListener('wheel', handleWheel, { passive: true });
    lastScrollTopRef.current = viewport.scrollTop;

    return () => {
      viewport.removeEventListener('scroll', handleScroll, true);
      viewport.removeEventListener('touchstart', handleTouchStart);
      viewport.removeEventListener('touchend', handleTouchEnd);
      viewport.removeEventListener('wheel', handleWheel);
      clearTimeout(scrollTimeout);
    };
  }, [scrollAreaRef]);

  useEffect(() => {
    const contentElement = contentRef.current;
    if (!contentElement) return;

    const resizeObserver = new ResizeObserver(() => {
      checkScroll();
    });

    resizeObserver.observe(contentElement);

    return () => {
      resizeObserver.disconnect();
    };
  }, [checkScroll]);

  return (
    <ScrollArea
      className={classNames?.base}
      componentProps={{
        viewport: {
          ref: scrollAreaRef,
          onScroll: checkScroll,
          className: '[overflow-anchor:none]',
        },
        ...props.componentProps,
      }}
      {...props}
    >
      <div ref={contentRef}>{children}</div>

      {showScrollButton && (
        <Button
          variant="secondary"
          size="icon"
          className={cn(classNames?.button, 'absolute bottom-5 left-1/2 -translate-x-1/2 rounded-full shadow-lg')}
          onClick={() => scrollToBottom({ smooth: true })}
        >
          <ArrowDown className="h-4 w-4" />
        </Button>
      )}
    </ScrollArea>
  );
}
