/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { Selection } from 'prosemirror-state';
import { NodeSelection } from 'prosemirror-state';
import type { EditorView } from 'prosemirror-view';
import { log } from '@/shared/core/log';

/**
 * 현재 selection이 math_inline 노드를 선택하고 있는지 확인하고 노드 정보를 반환
 */
export function getMathNodeAtSelection(view: EditorView, selection: Selection) {
  const { from } = selection;

  if (!(selection instanceof NodeSelection) || selection.node.type.name !== 'math_inline') {
    return null;
  }

  log.debug('math node selected');
  return {
    node: selection.node,
    view,
    getPos: () => from,
  };
}
