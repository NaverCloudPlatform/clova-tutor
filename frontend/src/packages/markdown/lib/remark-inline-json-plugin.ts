/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { Node, Parent } from 'unist';
import { visit } from 'unist-util-visit';
import type { CodeNode, TextNode } from '../types/ast';

const JSON_REGEX = /\{(?:[^{}]|(?:\{[^{}]*\}))*\}/g;

/**
 * @description
 * 직독직해 응답을 처리하는 remark 플러그인  
 *
 * @example 
 * 직독직해 응답은 모델 스트리밍에 다음과 같은 코드블럭 형태로 전달됩니다.
 ```json
{
    "type": "translation",
    "content": [
      { "en": "Some laws, *policies*, and practices", "ko": "\`일부 법률\`, \`정책\`, 그리고 \`관행\`은" },
      { "en": "are ~~developed~~", "ko": "만들어진다" },
      { "en": "without a <u>conscious intent to discriminate</u>", "ko": "**차별하려는 의식적인 의도** 없이" },
      { "en": "and may appear", "ko": "그리고 보일 수도 있다" },
      { "en": "ethnically neutral and impersonal", "ko": "인종적으로 중립적이고 비인격적인 것으로" }
    ]
}
```
 */
export function remarkInlineJson() {
  return (tree: Node) => {
    visit(tree, 'code', (node: CodeNode, index: number, parent: Parent) => {
      const value = node.value;

      if (node.lang !== 'json' || !JSON_REGEX.test(value)) return;

      const jsonMatches = value.match(JSON_REGEX) || [];
      const parts = jsonMatches.reduce<{
        tokens: string[];
        lastIndex: number;
      }>(
        (acc, match) => {
          const matchIndex = value.indexOf(match, acc.lastIndex);

          if (matchIndex > acc.lastIndex) {
            acc.tokens.push(value.substring(acc.lastIndex, matchIndex));
          }

          acc.tokens.push(match);

          return { tokens: acc.tokens, lastIndex: matchIndex + match.length };
        },
        { tokens: [], lastIndex: 0 },
      );

      if (parts.lastIndex < value.length) {
        parts.tokens.push(value.substring(parts.lastIndex));
      }

      const newNodes = parts.tokens.map((part) => {
        try {
          if (!part.trim().startsWith('{') || !part.trim().endsWith('}')) {
            return { type: 'text', value: part };
          }

          const parsed = JSON.parse(part);
          return {
            type: 'json-block',
            data: { hName: 'section', hProperties: { parsed } },
          };
        } catch {
          return { type: 'text', value: part };
        }
      });

      parent.children.splice(index, 1, ...(newNodes as TextNode[]));
    });
  };
}
