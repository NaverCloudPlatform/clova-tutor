import { kyInstance } from '@/shared/api/instance';

import { ProblemBookmarksApi } from './index';

const problemBookmarksApi = new ProblemBookmarksApi(kyInstance);

export { problemBookmarksApi };
