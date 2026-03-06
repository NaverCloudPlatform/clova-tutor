/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { Node } from 'prosemirror-model';
import { Plugin } from 'prosemirror-state';
import type { EditorView } from 'prosemirror-view';

import { eventManager } from '@/shared/core/event-manager';

import { MathNodeView } from './math-node-view';
import { transformPastedMath } from './utils/paste-transform';
import { getMathNodeAtSelection } from './utils/selection';

import 'katex/dist/katex.min.css';

export const mathNodePlugin = new Plugin({
  props: {
    nodeViews: {
      math_inline: (node: Node) => new MathNodeView(node),
    },

    transformPasted(slice, view) {
      return transformPastedMath(slice, view.state.schema);
    },
  },

  view() {
    const handleMathNodeFocus = (node: Node, view: EditorView, getPos: () => number) => {
      // DOM에서 해당 math 노드의 포털 컨테이너 찾기
      const pos = getPos();
      const domAt = view.domAtPos(pos);
      const mathContainer = domAt.node.parentElement?.querySelector(`[data-block-id="${node.attrs.blockId}"]`);
      const portalContainer = mathContainer?.querySelector('.math-portal-container') as HTMLDivElement;

      if (portalContainer) {
        // 포털 컨테이너 포인터 이벤트 활성화
        portalContainer.style.pointerEvents = 'auto';

        const closeHandler = () => {
          portalContainer.style.pointerEvents = 'none';
        };

        // eventManager를 통해 데이터 전달
        eventManager.emit('rich-editor:math-node-click', {
          container: portalContainer,
          blockId: node.attrs.blockId,
          latex: node.attrs.latex,
          view,
          getPos,
          close: closeHandler,
        });
      }
    };

    return {
      update(view: EditorView) {
        const currentSelection = view.state.selection;

        const mathNode = getMathNodeAtSelection(view, currentSelection);
        if (!mathNode) return;

        handleMathNodeFocus(mathNode.node, mathNode.view, mathNode.getPos);
      },
    };
  },
});
