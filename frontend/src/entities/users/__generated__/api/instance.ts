import { kyInstance } from '@/shared/api/instance';

import { UsersApi } from './index';

const usersApi = new UsersApi(kyInstance);

export { usersApi };
