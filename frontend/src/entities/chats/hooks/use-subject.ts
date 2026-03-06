/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useMatch } from '@tanstack/react-router';
import { SUBJECT_NAMES } from '@/shared/constants/subject';
import type { Subject } from '@/shared/types/common';

export function useSubject() {
  const isMathSubject = !!useMatch({
    from: '/_student/$subject',
    select: (match) => match.params.subject === 'math',
  });

  return {
    subject: (isMathSubject ? 'math' : 'english') as Subject,
    subjectName: isMathSubject ? SUBJECT_NAMES.math : SUBJECT_NAMES.english,
    isMathSubject,
    isEnglishSubject: !isMathSubject,
  } as const;
}
