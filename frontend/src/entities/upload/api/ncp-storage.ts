/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

/**
 * Nubes Storage 업로드
 *
 * @param url - 업로드 URL
 * @param file - 업로드 파일
 * @returns 업로드된 파일 URL
 * **/
export const postNubesStorage = async (url: string, file: File) => {
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': file.type || 'application/octet-stream',
      'x-amz-acl': 'public-read',
    },
    body: file,
  });

  const text = await res.text();

  return text;
};
