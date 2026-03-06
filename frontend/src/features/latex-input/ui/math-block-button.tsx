/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { SigmaIcon } from 'lucide-react';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import { Button } from '@/shared/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/shared/ui/tooltip';
import { cn } from '@/shared/utils/utils';

export function MathBlockButton() {
  const insertLatexInline = useRichEditorStore((state) => state.insertLatexInline);
  const { isMathSubject } = useSubject();

  const handleInsertLatexInline = () => {
    insertLatexInline('');
  };

  if (!isMathSubject) return null;

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          type="button"
          variant="outline"
          size="icon"
          aria-label="수식 블럭 삽입"
          className={cn('group text-foreground')}
          onClick={handleInsertLatexInline}
        >
          <SigmaIcon className="size-5 stroke-2 group-data-[state=on]:stroke-3" />
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>수식을 입력할 수 있어요</p>
      </TooltipContent>
    </Tooltip>
  );
}
