import type { KyInstance, Options } from 'ky';

import type {
  UploadFileUploadsKeyPutQueryParams,
  UploadUrlRequestDto,
  UploadUrlResponseDto,
} from '@/shared/api/__generated__/dto';
import { uploadUrlRequestDtoSchema, uploadUrlResponseDtoSchema } from '@/shared/api/__generated__/schema';
import { createSearchParams, validateSchema } from '@/shared/api/__generated__/utils';

export class UploadApi {
  private readonly instance: KyInstance;

  constructor(instance: KyInstance) {
    this.instance = instance;
  }

  /**
   * @tags upload
   * @summary Create Upload Url
   * @request POST:/uploads
   */
  async postUploads({ payload, kyInstance, options }: TUploadApiRequestParameters['postUploads']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(uploadUrlRequestDtoSchema, payload);

    const response = await instance
      .post<UploadUrlResponseDto>(`uploads`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(uploadUrlResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags upload
   * @summary Upload File
   * @request PUT:/uploads/{key}
   */
  async putUploadsByKey({ key, params, kyInstance, options }: TUploadApiRequestParameters['putUploadsByKey']) {
    const instance = kyInstance ?? this.instance;

    const urlSearchParams = createSearchParams(params);
    const response = await instance
      .put<any>(`uploads/${key}`, {
        searchParams: urlSearchParams,
        ...options,
      })
      .json();

    return response;
  }
}

export type TUploadApiRequestParameters = {
  postUploads: {
    payload: UploadUrlRequestDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  putUploadsByKey: {
    key: string;
    params: UploadFileUploadsKeyPutQueryParams;
    kyInstance?: KyInstance;
    options?: Options;
  };
};
