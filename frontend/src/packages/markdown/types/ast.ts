/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { Literal } from 'unist';

export interface TextNode extends Literal {
  type: 'text';
  value: string;
}

export interface CodeNode extends Literal {
  type: 'code';
  lang: string;
  value: string;
}
