/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { isString } from 'es-toolkit';
import type { DOMOutputSpec, Node, NodeSpec } from 'prosemirror-model';

export const mathNodeSchema: NodeSpec = {
  math_inline: {
    group: 'inline',
    inline: true,
    atom: true,
    attrs: {
      latex: { default: '' },
      blockId: { validate: isString },
    },
    parseDOM: [
      {
        tag: 'span[data-math]',
        getAttrs: (dom: HTMLElement) => ({
          latex: dom.getAttribute('data-latex'),
          blockId: dom.getAttribute('data-block-id'),
        }),
      },
    ],
    toDOM: (node: Node): DOMOutputSpec => [
      'span',
      {
        'data-math': 'true',
        'data-latex': node.attrs.latex,
        'data-block-id': node.attrs.blockId,
        class: 'math-inline',
      },
      node.attrs.latex,
    ],
    leafText: (node: Node) => ` $ ${node.attrs.latex} $ `,
  },
};
