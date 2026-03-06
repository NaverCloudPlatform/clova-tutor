import type { DefaultError, UseMutationOptions } from '@tanstack/react-query';
import { useMutation } from '@tanstack/react-query';

import type { UploadUrlResponseDto } from '@/shared/api/__generated__/dto';
import type { TUploadApiRequestParameters } from './index';
import { uploadApi } from './instance';

export const UPLOAD_MUTATION_KEY = {
  POST_UPLOADS: ['uploads'] as const,
  PUT_UPLOADS_KEY: ['uploads', 'key'] as const,
} as const;

const mutations = {
  postUploads: () => ({
    mutationFn: ({ payload, kyInstance, options }: TUploadApiRequestParameters['postUploads']) => {
      return uploadApi.postUploads({ payload, kyInstance, options });
    },
    mutationKey: UPLOAD_MUTATION_KEY.POST_UPLOADS,
    meta: {
      mutationFnName: 'postUploads',
    },
  }),
  putUploadsByKey: () => ({
    mutationFn: ({ key, params, kyInstance, options }: TUploadApiRequestParameters['putUploadsByKey']) => {
      return uploadApi.putUploadsByKey({ key, params, kyInstance, options });
    },
    mutationKey: UPLOAD_MUTATION_KEY.PUT_UPLOADS_KEY,
    meta: {
      mutationFnName: 'putUploadsByKey',
    },
  }),
};

export { mutations as uploadMutations };

/**
 * @tags upload
 * @summary Create Upload Url
 * @request POST:/uploads
 */
export const usePostUploadsMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<UploadUrlResponseDto, DefaultError, TUploadApiRequestParameters['postUploads'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.postUploads(),
    ...options,
  });
};

/**
 * @tags upload
 * @summary Upload File
 * @request PUT:/uploads/{key}
 */
export const usePutUploadsByKeyMutation = <TContext = unknown>(
  options?: Omit<
    UseMutationOptions<any, DefaultError, TUploadApiRequestParameters['putUploadsByKey'], TContext>,
    'mutationFn' | 'mutationKey'
  >,
) => {
  return useMutation({
    ...mutations.putUploadsByKey(),
    ...options,
  });
};
