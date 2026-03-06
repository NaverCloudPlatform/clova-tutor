import { kyInstance } from '@/shared/api/instance';

import { UploadApi } from './index';

const uploadApi = new UploadApi(kyInstance);

export { uploadApi };
