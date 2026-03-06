/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useEffect, useRef } from 'react';
import type { ImperativePanelHandle } from 'react-resizable-panels';
import { useIsMobile } from '@/shared/hooks/use-mobile';
import { cn } from '@/shared/utils/utils';
import { useStudyArea } from '../problem/-hooks/use-study-area';

export function useChatStudyAreaResize() {
  const chatPanelRef = useRef<ImperativePanelHandle>(null);
  const studyPanelRef = useRef<ImperativePanelHandle>(null);
  const { isStudyAreaOpen, closeStudyArea } = useStudyArea();
  const isMobile = useIsMobile();

  useEffect(() => {
    if (isMobile) {
      // 모바일: 학습 영역 열림 → 채팅 0, 학습 100
      if (isStudyAreaOpen) {
        studyPanelRef.current?.expand();
        chatPanelRef.current?.collapse();
        return;
      }

      // 모바일: 학습 영역 닫힘 → 채팅 100, 학습 0
      chatPanelRef.current?.expand();
      studyPanelRef.current?.collapse();
      return;
    }

    // 데스크톱: 학습 영역 열림 → 학습 50%
    if (isStudyAreaOpen) {
      studyPanelRef.current?.resize(50);
      return;
    }

    // 데스크톱: 학습 영역 닫힘 → 학습 0
    studyPanelRef.current?.collapse();
  }, [isStudyAreaOpen, isMobile]);

  const handleResize = (size: number) => {
    const studyAreaPanel = document.getElementById('study-area-panel');
    if (studyAreaPanel) {
      studyAreaPanel.style.transition = `none`;
    }
    if (!isMobile && size < 5) {
      closeStudyArea();
    }
  };

  const handleCollapse = () => {
    const studyAreaPanel = document.getElementById('study-area-panel');

    if (studyAreaPanel) {
      studyAreaPanel.style.transition = '';
    }
  };

  const chatPanelProps = {
    ref: chatPanelRef,
    defaultSize: isMobile && isStudyAreaOpen ? 0 : isMobile ? 100 : 50,
    minSize: isMobile ? 0 : 30,
    collapsible: isMobile,
  };
  const studyPanelProps = {
    ref: studyPanelRef,
    className: cn(
      'transition-all duration-700 cubic-bezier(0.4, 0, 0.2, 1)',
      'rounded-2xl mb-8',
      isStudyAreaOpen ? 'border mr-3' : 'border-none',
      isMobile ? 'ms-3 mt-3' : '',
    ),
    defaultSize: isMobile && isStudyAreaOpen ? 100 : isMobile ? 0 : isStudyAreaOpen ? 50 : 0,
    minSize: isMobile ? 0 : 35,
    collapsible: isMobile || !isStudyAreaOpen,
    onResize: handleResize,
    onCollapse: handleCollapse,
    onExpand: handleCollapse,
  };

  return {
    chatPanelProps,
    studyPanelProps,
    isResizeHandleVisible: isStudyAreaOpen && !isMobile,
    handleResize,
    handleCollapse,
  };
}
