/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { Callout } from '@r4ai/remark-callout';
import { BookmarkMinusIcon, BookOpenIcon, ClipboardPenLine, QuoteIcon } from 'lucide-react';
import { createContext, useCallback, useContext, useRef, useState } from 'react';
import { match, P } from 'ts-pattern';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/shared/ui/accordion';
import { cn } from '@/shared/utils/utils';

// 콜아웃 열림/닫힘 상태를 세션 동안 유지하기 위한 모듈 레벨 캐시
const calloutStateCache = new Map<string, string | undefined>();

type CalloutIdContextValue = {
  getNextId: () => string;
};

const CalloutIdContext = createContext<CalloutIdContextValue | null>(null);

/**
 * MarkdownBase 레벨에서 감싸서 각 콜아웃에 안정적인 ID를 부여합니다.
 * @param prefix - 메시지별 고유 식별자 (예: messageIndex)
 */
export function CalloutIdProvider({ prefix, children }: { prefix: string; children: React.ReactNode }) {
  const counterRef = useRef(0);
  // 매 렌더마다 카운터를 리셋하여 동일한 순서의 콜아웃에 동일한 ID 부여
  counterRef.current = 0;

  const getNextId = useCallback(() => {
    const id = `${prefix}-callout-${counterRef.current}`;
    counterRef.current += 1;
    return id;
  }, [prefix]);

  return <CalloutIdContext.Provider value={{ getNextId }}>{children}</CalloutIdContext.Provider>;
}

const calloutVariants = {
  quote: {
    classNames: {
      base: 'bg-muted',
      trigger: 'decoration-muted-foreground',
      title: 'text-muted-foreground',
    },
    icon: QuoteIcon,
    defaultTitle: 'quote',
  },
  note: {
    classNames: {
      base: 'bg-accent-blue-100',
      trigger: 'decoration-accent-blue-700',
      title: 'text-accent-blue-700',
    },
    icon: BookOpenIcon,
    defaultTitle: 'note',
  },
  passage: {
    classNames: {
      base: 'border',
      trigger: 'decoration-primary',
      title: 'text-muted-foreground',
    },
    icon: null,
    defaultTitle: '',
  },
  example: {
    classNames: {
      base: 'border',
      trigger: 'decoration-primary',
      title: 'text-muted-foreground',
    },
    icon: null,
    defaultTitle: '보기',
  },
  TABLE_FETCH: {
    classNames: {
      base: 'bg-muted',
      trigger: 'decoration-primary',
      title: 'text-primary',
    },
    icon: BookmarkMinusIcon,
    defaultTitle: '관련 학습자료 보기',
  },
  TRANSLATION: {
    classNames: {
      base: 'bg-muted',
      trigger: 'decoration-primary',
      title: 'text-primary',
    },
    icon: ClipboardPenLine,
    defaultTitle: '직독직해 보기',
  },
} as const;

const isCalloutType = (type: string): type is keyof typeof calloutVariants => {
  return type in calloutVariants;
};

export function CalloutComponent({ type, isFoldable, defaultFolded, children }: Callout & React.PropsWithChildren) {
  const context = useContext(CalloutIdContext);
  const calloutId = useRef(context?.getNextId() ?? '').current;

  const getInitialValue = () => {
    if (calloutId && calloutStateCache.has(calloutId)) {
      return calloutStateCache.get(calloutId);
    }
    return match([isFoldable, defaultFolded])
      .with([false, P._], () => 'item-1' as const)
      .with([true, false], () => 'item-1' as const)
      .with([true, true], () => undefined)
      .otherwise(() => 'item-1' as const);
  };

  const [value, setValue] = useState<string | undefined>(getInitialValue);

  const handleValueChange = (newValue: string) => {
    const resolved = newValue || undefined;
    setValue(resolved);
    if (calloutId) {
      calloutStateCache.set(calloutId, resolved);
    }
  };

  return (
    <Accordion
      type="single"
      collapsible
      value={value}
      onValueChange={handleValueChange}
      className={cn('w-full px-4 rounded-lg my-3', isCalloutType(type) ? calloutVariants[type].classNames.base : '')}
    >
      <AccordionItem value="item-1" disabled={!isFoldable}>
        {children}
      </AccordionItem>
    </Accordion>
  );
}

export function CalloutTitle({
  type,
  isFoldable,
  children,
}: Pick<Callout, 'type' | 'isFoldable'> & React.PropsWithChildren) {
  const Icon = isCalloutType(type) ? calloutVariants[type].icon : null;
  const isTitleEmpty = children?.toString().trim().toLocaleLowerCase() === type.toLowerCase();

  if (isCalloutType(type) && !calloutVariants[type].defaultTitle) {
    return <div className="h-4" />;
  }

  return (
    <AccordionTrigger
      className={cn(
        'flex items-center gap-2 font-semibold underline-offset-3',
        isCalloutType(type) ? calloutVariants[type].classNames.trigger : '',
        !isFoldable && '[&>svg]:hidden hover:no-underline disabled:opacity-100',
      )}
    >
      <div className={cn('flex items-center gap-2', isCalloutType(type) ? calloutVariants[type].classNames.title : '')}>
        {Icon && <Icon className="w-4 h-4" />}
        {isTitleEmpty ? (isCalloutType(type) ? calloutVariants[type].defaultTitle : null) : children}
      </div>
    </AccordionTrigger>
  );
}

export function CalloutBody({ children }: React.PropsWithChildren) {
  return <AccordionContent>{children}</AccordionContent>;
}
