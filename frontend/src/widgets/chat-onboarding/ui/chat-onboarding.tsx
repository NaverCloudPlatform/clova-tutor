/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Suspense } from 'react';
import { OnboardingQuestionList, OnboardingQuestionListSkeleton } from './onboarding-question-list';
import { OnboardingTitle } from './title';

type SubjectOnboardingProps = {
  subject: 'math' | 'english';
};

export function ChatOnboarding({ subject }: SubjectOnboardingProps) {
  const userId = localStorage.getItem('userId');

  return (
    <div className="flex-1 h-full flex flex-col justify-center sm:gap-y-28 gap-y-8 sm:py-20 py-6 px-4">
      <OnboardingTitle subject={subject} />
      {userId ? (
        <Suspense fallback={<OnboardingQuestionListSkeleton />}>
          <OnboardingQuestionList subject={subject} userId={userId} />
        </Suspense>
      ) : null}
    </div>
  );
}
