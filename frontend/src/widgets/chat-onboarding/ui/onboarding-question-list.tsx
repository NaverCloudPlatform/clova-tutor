/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useSuspenseQuery } from '@tanstack/react-query';
import { usersQueries } from '@/entities/users/__generated__/api/queries';
import type { SubjectEnumDto, UserResponseDto } from '@/shared/api/__generated__/dto';
import { Skeleton } from '@/shared/ui/skeleton';
import { ONBOARDING_CONFIG } from '../constants/onboarding-config';
import { selectRandomQuestions } from '../utils/select-random-questions';
import { OnboardingQuickstartButton } from './quickstart-input-button';

export type OnboardingQuestionListProps = {
  subject: SubjectEnumDto;
  userId: UserResponseDto['id'];
};

export function OnboardingQuestionList({ subject, userId }: OnboardingQuestionListProps) {
  const { data: user } = useSuspenseQuery({
    ...usersQueries.getUsersByUserId({
      userId: userId,
    }),
  });
  const questions = selectRandomQuestions(subject, user.grade, 3);
  const config = ONBOARDING_CONFIG[subject];

  return (
    <ul className="grid grid-cols-1 sm:grid-cols-3 gap-4" aria-label={config.ariaLabel}>
      {questions.map((question, index) => (
        <li key={question.id}>
          <OnboardingQuickstartButton prompt={question.prompt} questionNumber={index + 1} />
        </li>
      ))}
    </ul>
  );
}

export function OnboardingQuestionListSkeleton() {
  return (
    <ul className="grid grid-cols-3 gap-x-4">
      {Array.from({ length: 3 }).map((_, index) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: 스켈레톤
        <li key={index}>
          <Skeleton className="w-full h-42" />
        </li>
      ))}
    </ul>
  );
}
