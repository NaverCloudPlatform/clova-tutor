/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { toast } from 'sonner';
import { usePostUploadsMutation } from '../__generated__/api/mutations';
import { postNubesStorage } from '../api/ncp-storage';

type UploadFileOptions = {
  onSuccess: (url: string, file: File) => void;
  onError: (file: File) => void;
};

export function useNcpStorage() {
  const { mutateAsync: createUploadUrl } = usePostUploadsMutation();

  const uploadFile = async (file: File, options?: UploadFileOptions) => {
    try {
      const { presigned_url, file_url } = await createUploadUrl({
        payload: {
          mime_type: file.type,
        },
      });
      await postNubesStorage(presigned_url, file);

      options?.onSuccess(file_url, file);
    } catch (error) {
      toast.error('이미지 업로드에 실패했습니다.');
      console.error(error);
      options?.onError(file);
    }
  };

  return {
    uploadFile,
  };
}
