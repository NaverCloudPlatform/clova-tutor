/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { CheckIcon, CopyIcon } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/shared/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/shared/ui/tooltip';
import { copyToClipboard } from '@/shared/utils/clipboard';
import { cn } from '@/shared/utils/utils';

type CopyButtonProps = {
  copyContent: string;
  label?: string;
  tooltipContent?: React.ReactNode;
  buttonProps?: React.ComponentProps<typeof Button>;
};

export function CopyButton({ copyContent, label, tooltipContent, buttonProps }: CopyButtonProps) {
  const { className: buttonClassName, ...buttonRestProps } = buttonProps || {};
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    await copyToClipboard(copyContent);

    setIsCopied(true);
    setTimeout(() => {
      setIsCopied(false);
    }, 1200);
  };

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className={cn('text-muted-foreground', buttonClassName)}
          aria-label={isCopied ? '복사됨' : '복사하기'}
          onClick={isCopied ? undefined : handleCopy}
          disabled={isCopied}
          {...buttonRestProps}
        >
          {isCopied ? <CheckIcon /> : <CopyIcon />}
          {label}
        </Button>
      </TooltipTrigger>
      {!isCopied && <TooltipContent side="bottom">{tooltipContent || <p>복사</p>}</TooltipContent>}
    </Tooltip>
  );
}
