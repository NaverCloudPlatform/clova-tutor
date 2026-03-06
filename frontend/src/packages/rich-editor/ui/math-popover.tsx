/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { MathfieldElement } from 'mathlive';
import { TextSelection } from 'prosemirror-state';
import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { eventManager } from '@/shared/core/event-manager';
import { MathLive } from '@/shared/ui/mathlive';
import { Popover, PopoverContent, PopoverTrigger } from '@/shared/ui/popover';
import type { MathPortalInfo } from '../types/math-node';

export const MathPopover = () => {
  const [portalInfo, setPortalInfo] = useState<MathPortalInfo | null>(null);
  const mathFieldRef = useRef<MathfieldElement>(null);
  const isClosingRef = useRef(false); // NOTE: move-out으로 닫힐 때 handleOpenChange와 중복 호출 막기 위한 플래그
  const hadSuggestionRef = useRef(false); // NOTE: Enter 누르기 직전 suggestion popover 상태

  useEffect(() => {
    const handleMathNodeClick = (portalInfo: MathPortalInfo) => {
      setPortalInfo(portalInfo);
      isClosingRef.current = false;
    };

    eventManager.on('rich-editor:math-node-click', handleMathNodeClick);

    return () => {
      eventManager.off('rich-editor:math-node-click', handleMathNodeClick);
    };
  }, []);

  const closePopover = (direction: 'backward' | 'forward') => {
    if (!portalInfo || !mathFieldRef.current || isClosingRef.current) return;

    isClosingRef.current = true;

    const pos = portalInfo.getPos();

    if (!pos) {
      return;
    }

    const node = portalInfo.view.state.doc.nodeAt(pos);

    if (!node) {
      return;
    }

    const currentLatex = mathFieldRef.current.value?.trim() ?? '';

    // 수식이 비어있으면 노드 삭제
    if (currentLatex === '') {
      const tr = portalInfo.view.state.tr.delete(pos, pos + node.nodeSize);
      portalInfo.view.dispatch(tr);
      portalInfo.view.focus();

      mathFieldRef.current = null;
      portalInfo?.close();
      setPortalInfo(null);
      return;
    }

    const targetPos = direction === 'backward' ? pos : pos + node.nodeSize;
    const newSelection = TextSelection.create(portalInfo.view.state.doc, targetPos);
    const tr = portalInfo.view.state.tr.setSelection(newSelection);

    portalInfo.view.dispatch(tr);
    portalInfo.view.focus();

    mathFieldRef.current = null;
    portalInfo?.close();
    setPortalInfo(null);
  };

  const handleOpenChange = (open: boolean) => {
    if (open || isClosingRef.current) return;

    closePopover('forward');
  };

  const handleInput = (e: React.FormEvent<MathfieldElement>) => {
    const newLatex = e.currentTarget.value;

    if (portalInfo?.view && portalInfo?.getPos) {
      const pos = portalInfo.getPos();

      if (pos === undefined) {
        return;
      }

      const tr = portalInfo.view.state.tr.setNodeMarkup(pos, undefined, {
        latex: newLatex,
        blockId: portalInfo.blockId,
      });
      portalInfo.view.dispatch(tr);
    }
  };

  const handleKeyDownCapture = (e: React.KeyboardEvent<MathfieldElement>) => {
    if (e.key === 'Enter') {
      // 캡처 단계에서 suggestion popover 상태 확인 (MathLive가 처리하기 전)
      const suggestionPopover = document.getElementById('mathlive-suggestion-popover');
      const isVisible = suggestionPopover?.classList.contains('is-visible') ?? false;
      hadSuggestionRef.current = isVisible;
    }
  };

  const handleKeydown = (e: React.KeyboardEvent<MathfieldElement>) => {
    const close = () => {
      e.preventDefault();
      e.stopPropagation();
      closePopover('forward');
    };

    if (e.key === 'Escape') {
      close();
      return;
    }

    if (e.key === 'Enter') {
      if (hadSuggestionRef.current) {
        hadSuggestionRef.current = false;
        return;
      }

      close();
    }
  };

  const isClickInsideVirtualKeyboard = (e: {
    target: EventTarget | null;
    nativeEvent?: { target: EventTarget | null; composedPath?: () => EventTarget[] };
    detail?: { originalEvent?: { target: EventTarget | null; composedPath?: () => EventTarget[] } };
  }): boolean => {
    const originalEvent = e.detail?.originalEvent ?? e.nativeEvent ?? null;
    const path = originalEvent?.composedPath?.() ?? [];
    const eventTarget = originalEvent?.target ?? e.target;
    const targetsToCheck = path.length > 0 ? path : eventTarget instanceof Element ? [eventTarget] : [];

    return targetsToCheck.some((node) => {
      if (!(node instanceof Element)) return false;
      return !!(
        node.closest?.('#math-virtual-keyboard-container') ||
        node.closest?.('.ML__keyboard') ||
        node.classList?.contains('ML__keyboard')
      );
    });
  };

  const handlePointerDownOutside: Exclude<
    React.ComponentProps<typeof PopoverContent>['onPointerDownOutside'],
    undefined
  > = (e) => {
    if (isClickInsideVirtualKeyboard(e)) {
      e.preventDefault();
    }
  };

  const handleInteractOutside: Exclude<React.ComponentProps<typeof PopoverContent>['onInteractOutside'], undefined> = (
    e,
  ) => {
    if (isClickInsideVirtualKeyboard(e)) {
      e.preventDefault();
    }
  };

  if (!portalInfo) return null;

  return createPortal(
    <Popover open={!!portalInfo} onOpenChange={handleOpenChange}>
      <PopoverTrigger className="w-full h-full ring-2 ring-offset-1 ring-accent-blue-300 rounded" />
      <PopoverContent
        className="w-80 p-0"
        side="top"
        align="center"
        sideOffset={4}
        alignOffset={8}
        avoidCollisions
        onPointerDownOutside={handlePointerDownOutside}
        onInteractOutside={handleInteractOutside}
      >
        <MathLive
          ref={(ref) => {
            if (!ref) return;

            if (!mathFieldRef.current) {
              ref.selection = {
                ranges: [[0, -1]],
                direction: 'forward',
              };

              ref.addEventListener('move-out', (event) => {
                const direction = event.detail.direction as 'backward' | 'forward';

                closePopover(direction);
              });

              // 가상 키보드 엔터: mathlive에서 개행을 막고 dispatch하는 커스텀 이벤트 (keydown 없이 올 수 있음)
              ref.addEventListener('mathlive-enter-prevented', () => {
                const suggestionPopover = document.getElementById('mathlive-suggestion-popover');
                const isVisible = suggestionPopover?.classList.contains('is-visible') ?? false;

                if (!isVisible) {
                  closePopover('forward');
                }
              });
            }

            mathFieldRef.current = ref;
          }}
          onInput={handleInput}
          onKeyDownCapture={handleKeyDownCapture}
          onKeyDown={handleKeydown}
          className="min-w-60"
          classNames={{
            container: 'bg-card border-none',
          }}
        >
          {portalInfo.latex ?? ''}
        </MathLive>
      </PopoverContent>
    </Popover>,
    portalInfo.container,
  );
};
