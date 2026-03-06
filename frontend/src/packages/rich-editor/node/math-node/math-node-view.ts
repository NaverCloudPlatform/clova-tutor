/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import katex from 'katex';
import type { Node } from 'prosemirror-model';
import type { NodeView } from 'prosemirror-view';

export class MathNodeView implements NodeView {
  dom: HTMLElement;
  portalContainer: HTMLDivElement;

  constructor(node: Node) {
    // math-container 생성
    this.dom = document.createElement('span');
    this.dom.classList.add(
      'math-container',
      'inline-block',
      'cursor-pointer',
      'px-1',
      'py-0.5',
      'mx-0.5',
      'rounded',
      'hover:bg-muted',
      'transition-colors',
      'relative',
    );
    this.dom.setAttribute('data-block-id', node.attrs.blockId);
    this.dom.setAttribute('data-math-node', 'true');

    // math-container 내부에 math-portal-container 생성
    this.portalContainer = document.createElement('div');
    this.portalContainer.classList.add('math-portal-container', 'absolute', 'top-0', 'left-0', 'h-full', 'inset-0');
    this.dom.appendChild(this.portalContainer);

    // math-container 내부에 katex-container 생성
    this.renderKaTeX(node.attrs.latex);
  }

  private renderKaTeX(latex: string) {
    const katexContainer = document.createElement('span');

    if (latex?.trim()) {
      katex.render(latex, katexContainer, {
        throwOnError: false,
        displayMode: false,
        output: 'html',
        strict: 'ignore',
      });
    } else {
      katexContainer.textContent = '수식 입력';
      katexContainer.classList.add('text-sm', 'text-muted-foreground', 'italic', 'font-normal');
    }

    // 기존 katex-container 제거 안하면 입력 값 누적됨.
    const existingKatex = this.dom.querySelector('.katex-container');
    existingKatex?.remove();

    katexContainer.classList.add('katex-container');
    // NOTE: math-container > katex, portal 순서로 들어가야 수식 node 옆에서 한글 컴포징 문제 발생 안함. 원인 파악해야함.
    this.dom.insertAdjacentElement('beforeend', katexContainer);
    this.dom.setAttribute('data-latex', latex);
  }

  update(node: Node): boolean {
    this.renderKaTeX(node.attrs.latex);
    return true;
  }

  stopEvent(): boolean {
    return true;
  }

  destroy(): void {
    this.dom.remove();
    this.portalContainer.remove();
  }
}
