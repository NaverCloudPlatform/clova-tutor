import { kyInstance } from '@/shared/api/instance';

import { ProblemsApi } from './index';

const problemsApi = new ProblemsApi(kyInstance);

export { problemsApi };
