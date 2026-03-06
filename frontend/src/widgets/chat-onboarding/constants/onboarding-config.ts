/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export const ONBOARDING_CONFIG = {
  math: {
    title: {
      title: '수학 튜터',
      description: [
        '어떤 수학 문제든 정확하게 풀이 과정을 설명해줘요.',
        '답을 바로 알려주기보다, 단계별로 유도해서 스스로 풀 수 있게 도와줘요.',
        '이해가 부족한 개념은 쉽게 풀어 설명해 줘요.',
      ],
      image: '/icons/math.svg',
    },
    ariaLabel: '수학 예시 질문 목록',
  },
  english: {
    title: {
      title: '영어 튜터',
      description: [
        '어떤 영어 문제든 정확하게 풀이하고 설명해 줘요.',
        '문법 개념이 헷갈릴 땐, 기본 개념부터 예문을 통해 제대로 이해시켜줘요.',
        '영어 문장을 해석할 땐, 직독직해 방식으로 하나하나 짚어줘요.',
      ],
      image: '/icons/english.svg',
    },
    ariaLabel: '영어 예시 질문 목록',
  },
} as const;
