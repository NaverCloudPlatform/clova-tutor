/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

type GradeToNameOptions = {
  short?: boolean;
};

export const gradeToName = (grade: number, options?: GradeToNameOptions) => {
  const short = options?.short ?? false;

  if (grade >= 1 && grade <= 6) {
    const schoolName = short ? '초' : '초등학교';
    return short ? `${schoolName}${grade}` : `${schoolName} ${grade}학년`;
  }

  if (grade >= 7 && grade <= 9) {
    const schoolName = short ? '중' : '중학교';
    const gradeNumber = grade - 6;
    return short ? `${schoolName}${gradeNumber}` : `${schoolName} ${gradeNumber}학년`;
  }

  const schoolName = short ? '고' : '고등학교';
  const gradeNumber = grade - 9;
  return short ? `${schoolName}${gradeNumber}` : `${schoolName} ${gradeNumber}학년`;
};
