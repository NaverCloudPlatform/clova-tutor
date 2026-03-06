/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type ReactMarkdown from 'react-markdown';
import { match } from 'ts-pattern';
import type { CustomSectionType, TranslationSection } from '@/entities/chats/types/custom-section';
import { MarkdownBase } from '@/packages/markdown/ui/markdown-base';

type CustomSectionProps = {
  parsed?: CustomSectionType;
} & React.HTMLAttributes<HTMLElement>;

export function CustomSection({ parsed, ...props }: CustomSectionProps) {
  return (
    <div {...props}>
      {match(parsed)
        .with({ type: 'translation' }, (parsed) => <TranslationSectionComponent parsed={parsed} />)
        .otherwise((parsed) => {
          const { en, ko } = parsed as unknown as { en: string; ko: string };
          return (
            <div key={en} className="inline-flex flex-col">
              <p>
                {en}
                <span className="not-group-last:inline hidden">&nbsp;/&nbsp;</span>
              </p>
              <small className="text-muted-foreground">{ko}</small>
            </div>
          );
        })}
    </div>
  );
}

function TranslationSectionComponent({ parsed }: { parsed: TranslationSection }) {
  return (
    <div className="flex flex-wrap gap-x-1 gap-y-4">
      {parsed?.content.map((item) => (
        <div key={item.en} className="group/item flex gap-x-1.5">
          <div className="flex flex-col gap-y-1">
            <InlineMarkdown>{item.en}</InlineMarkdown>

            <small className="text-primary">
              <InlineMarkdown>{item.ko}</InlineMarkdown>
            </small>
          </div>
          <span className="text-muted-foreground group-last/item:hidden">/</span>
        </div>
      ))}
    </div>
  );
}

type InlineMarkdownProps = {
  children: React.ComponentProps<typeof MarkdownBase>['children'];
} & Pick<React.ComponentProps<typeof ReactMarkdown>, 'components'>;

function InlineMarkdown({ children }: InlineMarkdownProps) {
  return (
    <MarkdownBase
      components={{
        p: ({ ...props }) => <p {...props} className="inline-block" />,
      }}
    >
      {children}
    </MarkdownBase>
  );
}
