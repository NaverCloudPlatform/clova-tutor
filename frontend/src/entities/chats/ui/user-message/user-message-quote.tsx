/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { CornerDownRightIcon } from 'lucide-react';
import type { QuoteContentDto } from '@/shared/api/__generated__/dto';

type Props = {
  content: QuoteContentDto;
};

export function UserMessageQuote({ content }: Props) {
  return (
    <div className="flex justify-end gap-3 py-2 pt-3 ms-auto w-19/20">
      <CornerDownRightIcon className="size-4 flex-shrink-0" />
      <p className="text-sm text-muted-foreground line-clamp-3">{content.value.text}</p>
    </div>
  );
}
