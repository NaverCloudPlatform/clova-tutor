/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type React from 'react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Popover, PopoverAnchor, PopoverContent } from '@/shared/ui/popover';
import { cn } from '@/shared/utils/utils';
import { useIsMobile } from '../hooks/use-mobile';

interface SelectionPopoverProps extends React.PropsWithChildren {
  content: React.ReactNode | ((selectedFragment: DocumentFragment | null) => React.ReactNode);
  onTextSelected?: (text: string) => void;
  className?: string;
  /** 선택된 영역이 이 selector에 해당하는 요소 내부에 있으면 popover를 표시하지 않음 */
  ignoreSelector?: string;
}

export function SelectionPopoverWrapper({
  children,
  content,
  onTextSelected,
  className,
  ignoreSelector,
}: SelectionPopoverProps) {
  const isMobile = useIsMobile();
  const [open, setOpen] = useState(false);
  const [virtualRect, setVirtualRect] = useState<DOMRect | null>(null);
  const [selectedFragment, setSelectedFragment] = useState<DocumentFragment | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const updateSelection = useCallback(() => {
    const selection = window.getSelection();

    if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
      setOpen(false);
      return;
    }

    const range = selection.getRangeAt(0);
    const text = selection.toString().trim();

    if (!text || !containerRef.current?.contains(range.commonAncestorContainer)) {
      setOpen(false);
      return;
    }

    // ignoreSelector에 해당하는 영역에서는 popover를 표시하지 않음
    if (ignoreSelector) {
      const commonAncestor = range.commonAncestorContainer;
      const ancestorElement = commonAncestor instanceof Element ? commonAncestor : commonAncestor.parentElement;
      if (ancestorElement?.closest(ignoreSelector)) {
        setOpen(false);
        return;
      }
    }

    const rects = range.getClientRects();
    if (rects.length > 0) {
      setVirtualRect(rects[0]);
      // iOS Safari에서 버튼 클릭 시 selection이 해제되므로 미리 저장
      setSelectedFragment(range.cloneContents());
      setOpen(true);
      onTextSelected?.(text);
    }
  }, [onTextSelected, ignoreSelector]);

  useEffect(() => {
    const handleSelectionEnd = () => {
      requestAnimationFrame(updateSelection);
    };

    // 모바일에서 selectionchange로 텍스트 선택 감지
    const handleSelectionChange = () => {
      requestAnimationFrame(updateSelection);
    };

    document.addEventListener('mouseup', handleSelectionEnd);
    document.addEventListener('touchend', handleSelectionEnd);
    isMobile && document.addEventListener('selectionchange', handleSelectionChange);
    document.addEventListener('keyup', updateSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelectionEnd);
      document.removeEventListener('touchend', handleSelectionEnd);
      isMobile && document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('keyup', updateSelection);
    };
  }, [updateSelection, isMobile]);

  const virtualAnchorRef = useRef<{ getBoundingClientRect: () => DOMRect }>({
    getBoundingClientRect: () => new DOMRect(),
  });

  if (virtualRect) {
    virtualAnchorRef.current = {
      getBoundingClientRect: () => virtualRect,
    };
  }

  const handleContextMenu = useCallback((e: React.MouseEvent) => {
    const selection = window.getSelection();
    if (selection && !selection.isCollapsed) {
      e.preventDefault();
    }
  }, []);

  return (
    // biome-ignore lint/a11y/noStaticElementInteractions: 텍스트 선택 시 기본 컨텍스트 메뉴 숨김 처리
    <div ref={containerRef} className={cn('relative', className)} onContextMenu={handleContextMenu}>
      {children}

      <Popover open={open} onOpenChange={setOpen} modal={false}>
        <PopoverAnchor virtualRef={virtualAnchorRef as React.RefObject<{ getBoundingClientRect: () => DOMRect }>} />

        <PopoverContent
          side="top"
          align="center"
          sideOffset={10}
          onOpenAutoFocus={(e) => e.preventDefault()}
          onCloseAutoFocus={(e) => e.preventDefault()}
          onPointerDownCapture={(e) => e.stopPropagation()}
          className="w-fit p-1 shadow-lg"
        >
          {typeof content === 'function' ? content(selectedFragment) : content}
        </PopoverContent>
      </Popover>
    </div>
  );
}
