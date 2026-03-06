/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import 'katex/dist/katex.css';
import remarkCallout, { type Callout } from '@r4ai/remark-callout';
import React from 'react';
import ReactMarkdown, { type Components } from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { CalloutBody, CalloutComponent, CalloutTitle } from './callout';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './table';

type Props = React.ComponentProps<typeof ReactMarkdown> & {
  allowHtml?: boolean;
};

export function MarkdownBase({
  children,
  remarkPlugins,
  rehypePlugins,
  components,
  allowHtml = true,
  ...props
}: Props) {
  return (
    <ReactMarkdown
      remarkPlugins={[
        remarkMath,
        remarkGfm,
        [
          remarkCallout,
          {
            root: (callout: Callout) => ({
              tagName: 'callout',
              properties: {
                type: callout.type,
                isFoldable: callout.isFoldable,
                defaultFolded: callout.defaultFolded,
              },
            }),
            title: (callout: Callout) => ({
              tagName: 'callout-title',
              properties: {
                type: callout.type,
                isFoldable: callout.isFoldable,
              },
            }),
            body: () => ({
              tagName: 'callout-body',
            }),
          },
        ],
        ...(remarkPlugins || []),
      ]}
      rehypePlugins={[
        [rehypeKatex, { errorColor: '#42444b', strict: 'ignore' }],

        ...(allowHtml ? [rehypeRaw] : []),
        ...(rehypePlugins || []),
      ]}
      components={
        {
          callout: ({ ...props }) => (
            <CalloutComponent type={props.type} isFoldable={props.isFoldable} defaultFolded={props.defaultFolded}>
              {props.children}
            </CalloutComponent>
          ),
          'callout-title': ({ ...props }) => (
            <CalloutTitle type={props.type} isFoldable={props.isFoldable}>
              {props.children}
            </CalloutTitle>
          ),
          'callout-body': ({ ...props }) => <CalloutBody>{props.children}</CalloutBody>,
          blockquote: ({ ...props }) => <blockquote {...props} className="border-l-2 border-primary/40 pl-4" />,
          h1: ({ ...props }) => (
            <h1
              {...props}
              className="scroll-m-[1.25em] text-[2em] font-semibold tracking-tight lg:text-[3em] text-balance"
            />
          ),
          h2: ({ ...props }) => (
            <h2
              {...props}
              className="scroll-m-[1.25em] border-b pb-[0.125em] text-[1.6em] font-semibold tracking-tight first:mt-0"
            />
          ),
          h3: ({ ...props }) => (
            <h3 {...props} className="scroll-m-[1.25em] text-[1.4em] font-semibold tracking-tight" />
          ),
          h4: ({ ...props }) => (
            <h4 {...props} className="scroll-m-[1.25em] text-[1.25em] font-semibold tracking-tight" />
          ),
          h5: ({ ...props }) => (
            <h5 {...props} className="scroll-m-[1.25em] text-[1.125em] font-semibold tracking-tight" />
          ),
          h6: ({ ...props }) => <h6 {...props} className="scroll-m-[1.25em] text-[1em] font-normal tracking-tight" />,
          p: ({ ...props }) => (
            <p
              {...props}
              className="relative my-[0.5em] not-first:mt-[0.5em] leading-[1.75em] font-normal whitespace-pre-wrap"
            />
          ),
          ul: ({ ...props }) => <ul {...props} className="my-[1em] pl-[1.5em] list-disc [&>li]:mt-[0.5em]" />,
          ol: ({ ...props }) => <ol {...props} className="list-decimal list-inside not-first:mt-[0.5em]" />,
          li: ({ ...props }) => <li {...props} className="relative my-[0.5em] [&>p]:inline [&>p]:m-0" />,
          code: ({ 'aria-label': ariaLabel, ...props }) => {
            const { children, className } = props;
            const match = /language-(\w+)/.exec(className || '');

            if (ariaLabel === 'code-block') {
              return (
                <SyntaxHighlighter
                  language={match?.[1] ?? 'text'}
                  style={oneDark}
                  PreTag={(props) => <pre {...props} className="w-full block" />}
                  CodeTag={(props) => <code {...props} className="whitespace-pre-wrap!" />}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              );
            }

            return (
              <code
                {...props}
                className="whitespace-pre-wrap! bg-accent-yellow-200 text-accent-yellow-1000 font-semibold px-1 py-0.5 rounded-xs"
              />
            );
          },
          pre: ({ children, ...props }) => {
            return (
              React.isValidElement(children) && (
                <pre {...props} className="whitespace-pre-wrap">
                  {React.cloneElement(
                    children as React.ReactElement<
                      React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>
                    >,
                    {
                      'aria-label': 'code-block',
                    },
                  )}
                </pre>
              )
            );
          },
          a: ({ ...props }) => <a {...props} className="" />,
          strong: ({ ...props }) => <strong {...props} className="font-semibold" />,
          em: ({ ...props }) => <em {...props} className="" />,
          del: ({ ...props }) => <del {...props} className="" />,
          img: ({ alt, ...props }) => (
            <img {...props} alt={alt || ''} aria-label={alt || 'Markdown image'} className=" w-[7.5em] h-[7.5em]" />
          ),
          hr: ({ ...props }) => <hr {...props} className="my-[1em] border-t border-border" />,
          table: Table,
          thead: TableHeader,
          tbody: TableBody,
          tr: TableRow,
          th: TableHead,
          td: TableCell,
          u: ({ ...props }) => (
            <u {...props} className="text-primary underline font-semibold">
              {props.children}
            </u>
          ),
          ...components,
        } as Components
      }
      {...props}
    >
      {children?.trim()}
    </ReactMarkdown>
  );
}
