/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { ChatMarkdown } from '@/entities/chats/ui/chat-markdown';
import { Button } from '@/shared/ui/button';
import { Textarea } from '@/shared/ui/textarea';
import { CALLOUT_DUMMY, MARKDOWN_DUMMY, MARKDOWN_DUMMY_JSON } from '~/mocks/dummy/markdown';

export const Route = createFileRoute('/_student/$subject/chats/markdown')({
  component: RouteComponent,
});

const markdownDummyExamples = [
  {
    name: '직독직해 예시',
    value: MARKDOWN_DUMMY_JSON,
  },
  {
    name: 'Latex 예시',
    value: MARKDOWN_DUMMY,
  },
  {
    name: '콜아웃 예시',
    value: CALLOUT_DUMMY,
  },
];

function RouteComponent() {
  const [text, setText] = useState('');

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      <div className="flex flex-col gap-2">
        <p>Preview</p>
        <div className="border rounded-md min-h-50 px-4 py-2">
          <ChatMarkdown>{text}</ChatMarkdown>
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <p>Editor</p>
        <div className="flex flex-col gap-2 bg-muted p-2 rounded-md">
          <p>예시 버튼을 눌러보세요.</p>
          <div className="flex gap-2">
            {markdownDummyExamples.map((example) => (
              <Button key={example.name} variant="outline" onClick={() => setText(example.value)}>
                {example.name}
              </Button>
            ))}
          </div>
        </div>
        <Textarea
          id="markdown-editor"
          onChange={(e) => setText(e.target.value)}
          value={text}
          className="min-h-50"
          placeholder="마크다운 텍스트를 입력하면 왼쪽에 preview가 표시됩니다."
        />
      </div>
    </div>
  );
}
