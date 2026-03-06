/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export type TranslationSection = {
  type: 'translation';
  content: {
    en: string;
    ko: string;
  }[];
};

export type CustomSectionType = TranslationSection;
