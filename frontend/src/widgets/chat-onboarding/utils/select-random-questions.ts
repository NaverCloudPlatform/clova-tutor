/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { shuffle } from 'es-toolkit';
import { ONBOARDING_QUESTIONS } from '../constants/questions';

export function selectRandomQuestions(subject: 'math' | 'english', grade: number, count = 3) {
  const subjectQuestions = ONBOARDING_QUESTIONS[subject];
  const gradeKey = grade.toString() as keyof typeof subjectQuestions;
  const questions = subjectQuestions[gradeKey];

  if (!questions) return [];

  const shuffled = shuffle([...questions]);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}
