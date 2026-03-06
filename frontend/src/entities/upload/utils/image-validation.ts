/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { toast } from 'sonner';

const MAX_LONG_SIDE = 2240;
const MIN_SHORT_SIDE = 4;
const MAX_RATIO = 5;
const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB

const isValidImageFormat = (file: File) => {
  const validFormats = ['image/png', 'image/jpeg'];
  return validFormats.includes(file.type);
};

const isValidImageSize = (file: File) => {
  return file.size > 0 && file.size <= MAX_FILE_SIZE;
};

const isValidImageRatio = (width: number, height: number) => {
  const ratio = Math.max(width / height, height / width);
  return ratio <= MAX_RATIO;
};

const isValidImageLength = (width: number, height: number) => {
  const longSide = Math.max(width, height);
  const shortSide = Math.min(width, height);
  return longSide <= MAX_LONG_SIDE && shortSide >= MIN_SHORT_SIDE;
};

const canResizeToValid = (width: number, height: number) => {
  // 비율이 맞지 않으면 리사이즈해도 해결 불가
  if (!isValidImageRatio(width, height)) {
    return false;
  }

  // 리사이즈 후 짧은 쪽이 4px 미만이 되는지 확인
  const longSide = Math.max(width, height);
  const shortSide = Math.min(width, height);
  const scale = MAX_LONG_SIDE / longSide;
  const newShortSide = shortSide * scale;

  return newShortSide >= MIN_SHORT_SIDE;
};

const resizeImage = (img: HTMLImageElement, file: File): Promise<File> => {
  return new Promise((resolve, reject) => {
    const { width, height } = img;
    const longSide = Math.max(width, height);
    const scale = MAX_LONG_SIDE / longSide;

    const newWidth = Math.round(width * scale);
    const newHeight = Math.round(height * scale);

    const canvas = document.createElement('canvas');
    canvas.width = newWidth;
    canvas.height = newHeight;

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      reject(new Error('Canvas context를 생성할 수 없습니다.'));
      return;
    }

    ctx.drawImage(img, 0, 0, newWidth, newHeight);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error('이미지 변환에 실패했습니다.'));
          return;
        }

        const resizedFile = new File([blob], file.name, {
          type: file.type,
          lastModified: Date.now(),
        });

        resolve(resizedFile);
      },
      file.type,
      0.92,
    );
  });
};

export const isValidImageFile = (file: File): boolean | Promise<boolean> => {
  // 이미지 형식 검사: png, jpeg 형식만 허용
  if (!isValidImageFormat(file)) {
    toast.error('이미지 형식이 올바르지 않습니다.', {
      description: 'png 또는 jpeg 형식만 업로드할 수 있습니다.',
    });
    return false;
  }

  // 이미지 크기 검사: 0Byte 초과 20MB 이하
  if (!isValidImageSize(file)) {
    toast.error('이미지 크기가 올바르지 않습니다.', {
      description: '0Byte 초과 20MB 이하만 업로드할 수 있습니다.',
    });
    return false;
  }

  // 비율 및 길이 검사를 위한 이미지 로드
  return new Promise<boolean>((resolve) => {
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(objectUrl);

      // 비율 검사: 가로, 세로가 1:5 또는 5:1 이하
      if (!isValidImageRatio(img.width, img.height)) {
        toast.error('이미지 비율이 올바르지 않습니다.', {
          description: '가로, 세로가 1:5 또는 5:1 이하만 업로드할 수 있습니다.',
        });
        resolve(false);
        return;
      }

      // 길이 검사: 가로, 세로 중 긴 쪽은 2240px 이하, 짧은 쪽은 4px 이상
      if (!isValidImageLength(img.width, img.height)) {
        toast.error('이미지 길이가 올바르지 않습니다.', {
          description: '가로, 세로 중 긴 쪽은 2240px 이하,\n짧은 쪽은 4px 이상만 업로드할 수 있습니다.',
          classNames: {
            description: 'whitespace-pre-wrap break-keep',
          },
        });
        resolve(false);
        return;
      }

      resolve(true);
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(false);
    };

    img.src = objectUrl;
  });
};

/**
 * 이미지 검증 및 필요시 자동 리사이즈
 * @returns 유효한 File 또는 null (검증 실패 시)
 */
export const processImageFile = (file: File): Promise<File | null> => {
  // 이미지 형식 검사
  if (!isValidImageFormat(file)) {
    toast.error('이미지 형식이 올바르지 않습니다.', {
      description: 'png 또는 jpeg 형식만 업로드할 수 있습니다.',
    });
    return Promise.resolve(null);
  }

  // 이미지 크기 검사
  if (!isValidImageSize(file)) {
    toast.error('이미지 크기가 올바르지 않습니다.', {
      description: '0Byte 초과 20MB 이하만 업로드할 수 있습니다.',
    });
    return Promise.resolve(null);
  }

  return new Promise((resolve) => {
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = async () => {
      URL.revokeObjectURL(objectUrl);
      const { width, height } = img;

      // 비율 검사
      if (!isValidImageRatio(width, height)) {
        toast.error('이미지 비율이 올바르지 않습니다.', {
          description: '가로, 세로가 1:5 또는 5:1 이하만 업로드할 수 있습니다.',
        });
        resolve(null);
        return;
      }

      // 길이가 이미 유효하면 원본 반환
      if (isValidImageLength(width, height)) {
        resolve(file);
        return;
      }

      // 리사이즈 가능 여부 확인
      if (!canResizeToValid(width, height)) {
        toast.error('이미지 길이가 올바르지 않습니다.', {
          description: '가로, 세로 중 긴 쪽은 2240px 이하,\n짧은 쪽은 4px 이상만 업로드할 수 있습니다.',
          classNames: {
            description: 'whitespace-pre-wrap break-keep',
          },
        });
        resolve(null);
        return;
      }

      // 리사이즈 시도
      try {
        const resizedFile = await resizeImage(img, file);

        // 리사이즈 후 파일 크기 재검사
        if (!isValidImageSize(resizedFile)) {
          toast.error('이미지 크기가 올바르지 않습니다.', {
            description: '0Byte 초과 20MB 이하만 업로드할 수 있습니다.',
          });
          resolve(null);
          return;
        }

        resolve(resizedFile);
      } catch {
        toast.error('이미지 처리에 실패했습니다.');
        resolve(null);
      }
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      toast.error('이미지를 불러올 수 없습니다.');
      resolve(null);
    };

    img.src = objectUrl;
  });
};
