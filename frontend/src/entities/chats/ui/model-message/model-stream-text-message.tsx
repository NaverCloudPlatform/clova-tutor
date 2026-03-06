/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ChatMarkdown } from '@/entities/chats/ui/chat-markdown';
import { CustomSection } from '@/packages/markdown/ui/custom-section';
import { Table } from '@/packages/markdown/ui/table';
import type { TextContentDto } from '@/shared/api/__generated__/dto';
import { cn } from '@/shared/utils/utils';

type Props = {
  content: TextContentDto;
  messageId?: number;
};

function splitCompletedAndIncomplete(text: string) {
  const lastNewlineIndex = text.lastIndexOf('\n');

  if (lastNewlineIndex === -1) {
    return { completed: '', incomplete: text };
  }

  const incomplete = text.slice(lastNewlineIndex + 1);

  return {
    completed: text.slice(0, lastNewlineIndex + 1),
    incomplete: incomplete === '```' ? '' : incomplete,
  };
}

export function ModelStreamingTextMessage({ content, messageId }: Props) {
  const { completed, incomplete } = splitCompletedAndIncomplete(content.value.text);
  const calloutPrefix = messageId != null ? `msg-${messageId}` : undefined;

  const chatMarkdownComponent = {
    table: TableComponent,
    section: CustomSectionComponent,
  };

  return (
    <div className="my-2" data-streaming>
      <ChatMarkdown components={chatMarkdownComponent} calloutPrefix={calloutPrefix}>
        {completed}
      </ChatMarkdown>
      {incomplete && (
        <ChatMarkdown calloutPrefix={calloutPrefix ? `${calloutPrefix}-inc` : undefined}>{incomplete}</ChatMarkdown>
      )}
    </div>
  );
}

function CustomSectionComponent({ ...props }: React.ComponentProps<'section'>) {
  return <CustomSection {...props} className={cn('animate-in fade-in-0 duration-300')} />;
}

function TableComponent({ ...props }: React.ComponentProps<'table'>) {
  return <Table {...props} className={cn('animate-in fade-in-0 duration-300 slide-in-from-bottom-2')} />;
}
