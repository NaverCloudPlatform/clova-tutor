/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { DialogContent } from '@radix-ui/react-dialog';
import { Dialog, DialogDescription, DialogOverlay, DialogPortal, DialogTitle, DialogTrigger } from '@/shared/ui/dialog';
import { cn } from '@/shared/utils/utils';

type Props = React.ImgHTMLAttributes<HTMLImageElement>;

export function Image({ className, alt, ...props }: Props) {
  return (
    <div className="flex gap-1 justify-end">
      <Dialog>
        <DialogTrigger asChild>
          <img
            {...props}
            aria-label="이미지 미리보기"
            className={cn('max-h-[60dvh] rounded-lg object-contain cursor-pointer', className)}
            alt={alt}
          />
        </DialogTrigger>
        <DialogPortal data-slot="dialog-portal">
          <DialogOverlay />
          <DialogContent
            data-slot="dialog-content"
            className={cn(
              'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 duration-200',
              'bg-transparent fixed top-1/2 left-1/2 z-50 max-w-[80vw] w-max -translate-x-1/2 -translate-y-1/2 focus:outline-none',
            )}
          >
            <DialogTitle className="sr-only">첨부 파일</DialogTitle>
            <DialogDescription className="sr-only">{`${alt} 이미지`}</DialogDescription>
            <img {...props} alt={alt} className="w-auto min-h-[40dvh] max-h-[90dvh] h-auto object-contain" />
          </DialogContent>
        </DialogPortal>
      </Dialog>
    </div>
  );
}
