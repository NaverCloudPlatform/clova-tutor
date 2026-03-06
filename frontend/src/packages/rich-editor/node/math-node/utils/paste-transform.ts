/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { Node, Schema } from 'prosemirror-model';
import { Fragment, Slice } from 'prosemirror-model';
import { v4 as uuidv4 } from 'uuid';

// $$...$$ 형식과 $...$ 형식 모두 인식 ($$ 형식을 우선 매칭)
const MATH_REGEX = /\$\$([^$\n]+)\$\$|\$([^$\n]+)\$/g;

/**
 * 텍스트 노드를 파싱하여 수식($$...$$ 또는 $...$)을 math_inline 노드로 변환
 */
function parseTextNodeToMathFragments(textNode: Node, schema: Schema): Node[] {
  const text = textNode.text;
  if (!text) return [textNode];

  const matches = [...text.matchAll(MATH_REGEX)];
  if (matches.length === 0) return [textNode];

  const fragments: Node[] = [];
  let lastIndex = 0;

  for (const match of matches) {
    const matchStart = match.index || 0;
    const matchEnd = matchStart + match[0].length;

    // 수식 앞의 일반 텍스트 추가
    const beforeText = text.slice(lastIndex, matchStart);
    if (beforeText) {
      fragments.push(schema.text(beforeText));
    }

    // 수식을 math_inline 노드로 변환
    // match[1]은 $$ 형식, match[2]는 $ 형식
    const mathContent = (match[1] || match[2] || '').trim();
    if (mathContent) {
      fragments.push(
        schema.nodes.math_inline.create({
          latex: mathContent,
          blockId: uuidv4(),
        }),
      );
    }

    lastIndex = matchEnd;
  }

  // 마지막 수식 뒤의 일반 텍스트 추가
  const afterText = text.slice(lastIndex);
  if (afterText) {
    fragments.push(schema.text(afterText));
  }

  return fragments;
}

/**
 * 노드를 재귀적으로 처리하여 수식을 변환
 */
function processNode(node: Node, schema: Schema): Node[] {
  if (node.isText) {
    return parseTextNodeToMathFragments(node, schema);
  }

  // 자식 노드가 있는 경우 재귀적으로 처리
  if (node.content && node.content.size > 0) {
    const newContent: Node[] = [];
    node.content.forEach((child: Node) => {
      newContent.push(...processNode(child, schema));
    });

    if (newContent.length > 0) {
      return [node.type.create(node.attrs, newContent)];
    }
  }

  return [node];
}

/**
 * 붙여넣기된 컨텐츠에서 $$...$$ 또는 $...$ 형식의 수식을 math_inline 노드로 변환
 */
export function transformPastedMath(slice: Slice, schema: Schema): Slice {
  const { content } = slice;

  const newNodes: Node[] = [];
  content.forEach((node: Node) => {
    newNodes.push(...processNode(node, schema));
  });

  // 변경사항이 있는 경우에만 새로운 슬라이스 반환
  const hasChanges = newNodes.some((node: Node, index: number) => node !== content.child(index));

  if (hasChanges) {
    return new Slice(Fragment.from(newNodes), slice.openStart, slice.openEnd);
  }

  return slice;
}
