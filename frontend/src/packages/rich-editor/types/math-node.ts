/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { EditorView } from 'prosemirror-view';

export type MathPortalInfo = {
  container: HTMLDivElement;
  blockId: string;
  latex: string;
  view: EditorView;
  getPos: () => number | undefined;
  close: () => void;
};
