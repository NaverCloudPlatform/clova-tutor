/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { TChatsApiRequestParameters } from '@/entities/chats/__generated__/api';

export type ProblemBookProps = {
  problemId: TChatsApiRequestParameters['getChatsByChatIdProblemsByProblemId']['problemId'];
  chatId: TChatsApiRequestParameters['getChatsByChatIdProblemsByProblemId']['chatId'];
};
