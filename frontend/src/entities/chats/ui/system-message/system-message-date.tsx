/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Badge } from '@/shared/ui/badge';

type SystemMessaegDateProps = {
  date: string;
};

export function SystemMessaegDate({ date }: SystemMessaegDateProps) {
  return (
    <Badge variant="secondary" className="mx-auto">
      {date}
    </Badge>
  );
}
