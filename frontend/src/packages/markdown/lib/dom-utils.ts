/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import TurndownService from 'turndown';

export const findKatexAncestor = (node: Node | null): Element | null => {
  const current = node?.nodeType === Node.TEXT_NODE ? node?.parentElement : (node as Element);

  if (!current || current === document.body) return null;

  if (current.tagName === 'SPAN' && current.classList.contains('katex')) {
    return current;
  }

  return findKatexAncestor(current.parentElement);
};

// turndown 인스턴스 생성 및 설정
const turndownService = new TurndownService({
  headingStyle: 'atx', // # 형태의 헤딩 사용
  codeBlockStyle: 'fenced', // ``` 형태의 코드블록 사용
  bulletListMarker: '-', // - 형태의 리스트 마커 사용
  emDelimiter: '*', // *italic* 형태 사용
  strongDelimiter: '**', // **bold** 형태 사용
});

// KaTeX 수식 처리를 위한 커스텀 규칙 추가
turndownService.addRule('katex', {
  filter: (node) => node.nodeName === 'SPAN' && node.classList && node.classList.contains('katex'),
  replacement: (content, node) => {
    const latex = node.querySelector(
      'span.katex-mathml > math > semantics > annotation[encoding="application/x-tex"]',
    )?.textContent;
    return latex ? `$ ${latex} $` : content;
  },
});

export const nodeToMarkdown = (node: Node): string => {
  // turndown을 사용하여 간단하게 변환
  if (node.nodeType === Node.ELEMENT_NODE) {
    return turndownService.turndown(node as HTMLElement);
  }

  if (node.nodeType === Node.TEXT_NODE) {
    return node.textContent || '';
  }

  return '';
};

export const fragmentToMarkdown = (cachedFragment?: DocumentFragment | null): string => {
  let fragment: DocumentFragment | null = cachedFragment ?? null;

  // cachedFragment가 없으면 현재 selection에서 가져옴
  if (!fragment) {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return '';

    const range = selection.getRangeAt(0);
    fragment = range.cloneContents();
  }

  // fragment를 임시 div에 추가하여 turndown으로 변환
  const tempDiv = document.createElement('div');
  tempDiv.appendChild(fragment.cloneNode(true));

  // turndown을 사용하여 HTML을 마크다운으로 변환
  const markdown = turndownService.turndown(tempDiv);

  return markdown.trim();
};
