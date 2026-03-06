/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { NodeSelection } from 'prosemirror-state';
import type { EditorView } from 'prosemirror-view';
import { v4 as uuidv4 } from 'uuid';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import { insertTextWithLineBreaks } from '../node/math-node/utils/latex';

// 🏪 Zustand Store 정의
interface RichEditorStore {
  editor: EditorView | null;
  setEditor: (editorView: EditorView | null) => void;

  isEmpty: boolean;
  setIsEmpty: (isEmpty: boolean) => void;

  // 텍스트 관련 메서드
  getText: () => string;
  insertText: (text: string) => void;
  insertLatexInline: (latex: string) => void;
  deleteAll: () => void;
  focus: () => void;
}

export const useRichEditorStore = create<RichEditorStore>()(
  devtools(
    (set, get) => ({
      editor: null,
      setEditor: (editor) => set({ editor }, false, 'setEditor'),

      isEmpty: true,
      setIsEmpty: (isEmpty: boolean) => set({ isEmpty }, false, 'setIsEmpty'),

      getText: () => {
        const { editor } = get();
        if (!editor) return '';

        const doc = editor.state.doc;
        return doc.textBetween(0, doc.nodeSize - 2, '\n');
      },

      insertText: (_text: string) => {
        const { editor } = get();
        if (!editor) return;

        const { state, dispatch } = editor;
        const { selection } = state;
        const text = _text.trim();

        const tr = state.tr.deleteSelection();
        insertTextWithLineBreaks(text, state, tr, selection.from);

        dispatch(tr);

        const isMobile = window.matchMedia('(max-width: 768px)').matches;
        if (!isMobile) {
          editor.focus();
        }
      },

      insertLatexInline: (latex: string) => {
        const { editor } = get();
        if (!editor) return;

        const { state, dispatch } = editor;
        const { schema, selection } = state;
        const { from, to } = selection;

        const mathNode = schema.nodes.math_inline.create({
          latex,
          blockId: uuidv4(),
        });
        const tr = state.tr.replaceRangeWith(from, to, mathNode);

        // 삽입된 수식 노드를 NodeSelection으로 선택하여 자동으로 popover가 열리도록 함
        const newPos = from;
        tr.setSelection(NodeSelection.create(tr.doc, newPos));

        dispatch(tr);
      },

      deleteAll: () => {
        const { editor } = get();
        if (!editor) return;

        const { state, dispatch } = editor;
        const tr = state.tr.delete(0, state.doc.content.size);

        dispatch(tr);
      },

      focus: () => {
        const { editor } = get();
        if (!editor) return;

        editor.focus();
      },
    }),
    { name: 'RichEditorStore', enabled: import.meta.env.DEV },
  ),
);
