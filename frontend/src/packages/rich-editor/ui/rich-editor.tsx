/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { baseKeymap } from 'prosemirror-commands';
import { history } from 'prosemirror-history';
import { keymap } from 'prosemirror-keymap';
import { Schema } from 'prosemirror-model';
import { EditorState } from 'prosemirror-state';
import { EditorView } from 'prosemirror-view';
import { useEffect, useRef, useState } from 'react';

import 'prosemirror-view/style/prosemirror.css';
import 'mathlive/fonts.css';
import 'mathlive/static.css';
import { useShallow } from 'zustand/shallow';
import { cn } from '@/shared/utils/utils';
import { mathNodePlugin } from '../node/math-node/math-node-plugin';
import { mathNodeSchema } from '../node/math-node/math-node-schema';
import { insertTextWithLineBreaks } from '../node/math-node/utils/latex';
import { useRichEditorStore } from '../store/use-rich-editor-store';
import { MathPopover } from './math-popover';

const schema = new Schema({
  nodes: {
    doc: { content: 'block+' },
    paragraph: {
      group: 'block',
      content: 'inline*',
      parseDOM: [{ tag: 'p' }],
      toDOM: () => ['p', 0],
    },
    text: { group: 'inline' },
    math_inline: mathNodeSchema.math_inline,
  },
});

type Props = {
  className?: string;
  defaultValue?: string;
  children?: React.ReactNode;
};

export const RichEditor = ({ className, defaultValue, children }: Props) => {
  const { setEditor, setIsEmpty } = useRichEditorStore(
    useShallow((state) => ({
      setEditor: state.setEditor,
      setIsEmpty: state.setIsEmpty,
      isEmpty: state.isEmpty,
    })),
  );
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [isInitial, setIsInitial] = useState(true);

  useEffect(() => {
    if (!editorRef.current) return;

    const state = EditorState.create({
      schema,
      plugins: [
        history(),
        keymap({
          ...baseKeymap,
          Enter: (_, __, view) => {
            const form = view?.dom.closest('form');

            if (form) {
              const submitButton =
                form.querySelector<HTMLButtonElement>('button[type="submit"]') ||
                form.querySelector<HTMLInputElement>('input[type="submit"]');

              if (submitButton?.disabled) {
                return true;
              }

              // form의 submit 이벤트를 트리거
              const submitEvent = new Event('submit', {
                bubbles: true,
                cancelable: true,
              });
              form.dispatchEvent(submitEvent);
            }

            return true;
          },
          'Shift-Enter': (state, dispatch) => {
            if (dispatch) {
              const { schema, selection } = state;
              const { $from } = selection;

              if ($from.parent.type === schema.nodes.paragraph) {
                const tr = state.tr.split($from.pos);
                dispatch(tr);
                return true;
              }
            }
            return false;
          },
        }),
        mathNodePlugin,
      ],
    });

    viewRef.current = new EditorView(editorRef.current, {
      state,
      attributes: {
        class: cn(className, 'focus:outline-none'),
      },
      dispatchTransaction: (tr) => {
        if (!viewRef.current) return;

        const newState = viewRef.current.state.apply(tr);
        viewRef.current.updateState(newState);

        if (tr.docChanged) {
          const textContent = newState.doc.textContent.trim();
          const isInitial = newState.doc.content.size <= 2;
          const empty = isInitial || textContent === '';
          setIsInitial(isInitial);
          setIsEmpty(empty);
        }
      },
    });

    if (defaultValue) {
      setIsEmpty(false);
      setIsInitial(false);

      const tr = viewRef.current.state.tr;
      insertTextWithLineBreaks(defaultValue, viewRef.current.state, tr, 0);
      viewRef.current.dispatch(tr);
    }

    setEditor(viewRef.current);

    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    if (!isMobile) {
      viewRef.current.focus();
    }

    // 테스트 환경에서 EditorView 접근 가능하도록 노출
    if (import.meta.env.DEV || import.meta.env.MODE === 'test') {
      (window as Window & { __editorView?: EditorView }).__editorView = viewRef.current;
    }

    return () => {
      setEditor(null);
      if (import.meta.env.DEV || import.meta.env.MODE === 'test') {
        delete (window as Window & { __editorView?: EditorView }).__editorView;
      }
      viewRef.current?.destroy();
    };
  }, [setEditor, setIsEmpty, className, defaultValue]);

  return (
    <>
      <div className="relative">
        <div ref={editorRef} />
        {isInitial && <div className="absolute left-2 top-1 text-muted-foreground pointer-events-none">{children}</div>}
      </div>

      {/* Portal 기반 팝오버 */}
      <MathPopover />
    </>
  );
};
