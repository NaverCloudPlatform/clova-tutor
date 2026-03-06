/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useEffect } from 'react';
import { findKatexAncestor } from '../lib/dom-utils';

export function useKatexSelection() {
  useEffect(() => {
    const handleSelect = () => {
      const selection = window.getSelection();
      if (!selection || !selection.rangeCount) return;

      const range = selection.getRangeAt(0);

      // 선택이 비어있으면 처리하지 않음
      if (range.collapsed) return;

      const startKatex = findKatexAncestor(range.startContainer);
      const endKatex = findKatexAncestor(range.endContainer);

      // katex 요소가 없으면 처리하지 않음
      if (!startKatex && !endKatex) return;

      const isBackward =
        selection.anchorNode &&
        selection.focusNode &&
        selection.anchorNode.compareDocumentPosition(selection.focusNode) & Node.DOCUMENT_POSITION_PRECEDING;

      const newRange = document.createRange();

      startKatex
        ? newRange.setStartBefore(startKatex) //katex 포함 range로 갱신
        : newRange.setStart(range.startContainer, range.startOffset); //현재 range와 동일하게 유지 하기 위해
      endKatex ? newRange.setEndAfter(endKatex) : newRange.setEnd(range.endContainer, range.endOffset);

      selection.removeAllRanges();
      selection.addRange(newRange);

      // 역방향 선택이었다면 방향을 유지
      if (isBackward && selection.extend) {
        const tempRange = newRange.cloneRange();
        selection.removeAllRanges();
        selection.addRange(tempRange);

        // 선택 방향을 역방향으로 설정
        selection.collapseToEnd();
        selection.extend(tempRange.startContainer, tempRange.startOffset);
      }
    };

    document.addEventListener('selectionchange', handleSelect);

    return () => {
      document.removeEventListener('selectionchange', handleSelect);
    };
  }, []);
}
