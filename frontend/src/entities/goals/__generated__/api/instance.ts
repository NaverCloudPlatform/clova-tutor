import { kyInstance } from '@/shared/api/instance';

import { GoalsApi } from './index';

const goalsApi = new GoalsApi(kyInstance);

export { goalsApi };
