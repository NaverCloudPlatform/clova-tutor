/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { SubjectEnumDto } from '@/shared/api/__generated__/dto';
import { ONBOARDING_CONFIG } from '../constants/onboarding-config';

type OnboardingTitleProps = {
  subject: SubjectEnumDto;
};

export function OnboardingTitle({ subject }: OnboardingTitleProps) {
  const config = ONBOARDING_CONFIG[subject];

  return (
    <div className="flex flex-col gap-y-6">
      <div className="flex flex-col gap-y-5">
        <img
          src={config.title.image}
          alt={`${config.title.title} 로고 이미`}
          width={80}
          height={80}
          className="h-13 w-13 ms-0.5"
        />
        <h1 className="text-2xl font-semibold">{config.title.title}</h1>
      </div>
      <div className="text-foreground-weak flex flex-col gap-y-2">
        {config.title.description.map((line) => (
          <p key={line}>{line}</p>
        ))}
      </div>
    </div>
  );
}
