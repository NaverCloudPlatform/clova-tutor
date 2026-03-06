import { kyInstance } from '@/shared/api/instance';

import { ChatsApi } from './index';

const chatsApi = new ChatsApi(kyInstance);

export { chatsApi };
