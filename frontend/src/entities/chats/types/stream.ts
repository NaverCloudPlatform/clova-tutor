/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { z } from 'zod';
import type { messageDeltaDataSchema } from '../schema/stream';

export type MessageDeltaData = z.infer<typeof messageDeltaDataSchema>;
