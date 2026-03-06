/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export const isKoreaCharacter = (char: string) => {
  return /[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/.test(char);
};

export const removeKoreanCharacters = (text: string): string => {
  return text.replace(/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/g, '');
};

export const isJsonString = (str: string): boolean => {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
};
