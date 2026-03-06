/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { z } from 'zod';

export const messageDeltaDataSchema = z.object({
  text: z.string(),
});
