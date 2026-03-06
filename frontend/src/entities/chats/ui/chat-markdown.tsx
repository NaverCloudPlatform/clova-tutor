/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type ReactMarkdown from 'react-markdown';
import { remarkInlineJson } from '@/packages/markdown/lib/remark-inline-json-plugin';
import { CalloutIdProvider } from '@/packages/markdown/ui/callout';
import { CustomSection } from '@/packages/markdown/ui/custom-section';
import { MarkdownBase } from '@/packages/markdown/ui/markdown-base';
import { cn } from '@/shared/utils/utils';

type Props = {
  children: React.ComponentProps<typeof MarkdownBase>['children'];
  calloutPrefix?: string;
} & Pick<React.ComponentProps<typeof ReactMarkdown>, 'components'>;

export function ChatMarkdown({ children, components, calloutPrefix }: Props) {
  const content = (
    <MarkdownBase
      remarkPlugins={[remarkInlineJson]}
      allowHtml={false}
      components={{
        section: CustomSection,
        p: ({ ...props }) => (
          <p {...props} className={cn('relative not-first:mt-3 not-first:mb-2 leading-7.5 whitespace-pre-wrap')} />
        ),
        ...components,
      }}
    >
      {children}
    </MarkdownBase>
  );

  if (calloutPrefix) {
    return <CalloutIdProvider prefix={calloutPrefix}>{content}</CalloutIdProvider>;
  }

  return content;
}
