/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { inRange } from 'es-toolkit';
import { DIFFICULTY_LEVEL } from '../constants/difficulty';

export function getDifficultyLevelText(level: number): number | null {
  if (inRange(level, DIFFICULTY_LEVEL.LOW.min, DIFFICULTY_LEVEL.LOW.max + 1)) {
    return 1;
  }
  if (inRange(level, DIFFICULTY_LEVEL.MEDIUM.min, DIFFICULTY_LEVEL.MEDIUM.max + 1)) {
    return 2;
  }
  if (inRange(level, DIFFICULTY_LEVEL.HIGH.min, DIFFICULTY_LEVEL.HIGH.max + 1)) {
    return 3;
  }
  return null;
}
