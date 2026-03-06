/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type React from 'react';
import type { MessageMetadataResponseDto } from '@/shared/api/__generated__/dto';
import { IS_LOCAL } from '@/shared/constants/env';
import { Badge } from '@/shared/ui/badge';

type ModelMessageBadgeProps = {
  messageMetadata?: MessageMetadataResponseDto;
  dev?: boolean;
} & React.ComponentProps<'div'>;

export function ModelMessageBadge({ messageMetadata, dev }: ModelMessageBadgeProps) {
  return (
    dev &&
    IS_LOCAL && (
      <Badge variant='secondary'>
        {messageMetadata?.tools?.length ? messageMetadata?.tools?.map((tool) => tool.name).join(', ') : 'no tools'}
      </Badge>
    )
  );
}
