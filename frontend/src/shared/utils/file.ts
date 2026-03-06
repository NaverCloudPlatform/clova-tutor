/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { log } from '../core/log';

type UtilOptions = {
  throwOnError?: boolean;
};

export const convertImageUrlToFile = async (image: string, { throwOnError = false }: UtilOptions) => {
  try {
    const response = await fetch(image);
    const blob = await response.blob();
    const fileName = image.split('/').pop() || 'image.png';
    const file = new File([blob], fileName, { type: blob.type });
    return file;
  } catch (error) {
    log.error(error);

    if (throwOnError) {
      throw error;
    }
  }

  return null;
};
