/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

/**
 * 클립보드에 텍스트를 복사하는 유틸 함수
 * HTTP와 HTTPS 환경 모두에서 동작합니다.
 *
 * @param text - 클립보드에 복사할 텍스트
 * @returns Promise<boolean> - 복사 성공 여부
 */
export async function copyToClipboard(text: string) {
  try {
    // HTTPS 환경에서 clipboard API 사용
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    // HTTP 환경에서 fallback: 텍스트 선택 방식 사용
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
      const success = document.execCommand('copy');
      return success;
    } finally {
      document.body.removeChild(textArea);
    }
  } catch (err) {
    console.error('Clipboard copy failed:', err);
    return false;
  }
}
