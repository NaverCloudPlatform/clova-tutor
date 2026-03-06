/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { compact } from 'es-toolkit';
import type { EditorState, Transaction } from 'prosemirror-state';
import { v4 as uuidv4 } from 'uuid';

/**
 * 텍스트에 LaTeX 수식이 포함되어 있는지 확인
 */
export function hasLatexInText(text: string): boolean {
  return /\$\$[^$\n]+\$\$|\$[^$\n]+\$/.test(text);
}

/**
 * LaTeX 수식과 일반 텍스트를 모두 처리하는 텍스트 삽입 (줄바꿈 포함)
 */
export function insertTextWithLineBreaks(text: string, state: EditorState, tr: Transaction, startPos: number): number {
  if (!text) return startPos;

  const lines = text.split('\n');

  // 모든 줄을 통일된 방식으로 처리
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // 첫 번째 줄이 아닌 경우에만 단락 분리
    if (i > 0) {
      const currentPos = tr.selection.to;
      const $pos = tr.doc.resolve(currentPos);

      if ($pos.parent.type === state.schema.nodes.paragraph) {
        tr.split(currentPos);
      }
    } else {
      // 첫 번째 줄의 경우 시작 위치로 커서 이동
      tr.insertText('', startPos, startPos);
    }

    // 각 줄에서 LaTeX와 일반 텍스트 처리 (빈 줄이어도 처리)
    if (line) {
      // $$...$$ 형식과 $...$ 형식 모두 인식 ($$ 형식을 우선 매칭)
      const parts = compact(line.split(/(\$\$[^$]*\$\$|\$[^$]*\$)/g));

      for (const part of parts) {
        if (
          (part.startsWith('$$') && part.endsWith('$$') && part.length > 4) ||
          (part.startsWith('$') && part.endsWith('$') && part.length > 2)
        ) {
          // LaTeX 수식으로 처리 (자동 위치 추적)
          // $$ 형식이면 앞뒤 2개씩, $ 형식이면 앞뒤 1개씩 제거
          const latex = part.startsWith('$$') ? part.slice(2, -2).trim() : part.slice(1, -1).trim();
          const mathNode = state.schema.nodes.math_inline.create({
            latex,
            blockId: uuidv4(),
          });

          // 현재 커서 위치에 삽입 (nodeSize 계산 없이)
          tr.insert(tr.selection.to, mathNode);
        } else if (part) {
          // 일반 텍스트로 처리 (자동 위치 추적)
          tr.insertText(part.trim());
        }
      }
    }
  }

  return tr.selection.to;
}
