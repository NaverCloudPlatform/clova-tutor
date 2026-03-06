/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { compact } from 'es-toolkit';
import type { ImagesContentDto } from '@/shared/api/__generated__/dto';
import { Image } from '@/shared/ui/images';
import { cn } from '@/shared/utils/utils';

type Props = {
  images?: ImagesContentDto['value']['sources'];
};

export function ChatImages({ images }: Props) {
  if (!images) return null;

  return (
    <div className="flex gap-1 justify-end">
      {compact(images).map((image) => {
        const isClearImage = image.endsWith('clear.png');

        return (
          <Image
            key={image}
            src={image}
            alt="채팅 첨부 파일"
            width={300}
            className={cn(isClearImage ? 'bg-[#2F4931]' : 'bg-transparent')}
          />
        );
      })}
    </div>
  );
}
