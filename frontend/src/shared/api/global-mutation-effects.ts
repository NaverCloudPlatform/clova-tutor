/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { InfiniteData, QueryClient } from '@tanstack/react-query';
import { queryClient } from '@/app/provider/tanstack-query';
import { chatsQueries, chatsQueryKeys } from '@/entities/chats/__generated__/api/queries';
import {
  problemBookmarksQueries,
  problemBookmarksQueryKeys,
} from '@/entities/problem-bookmarks/__generated__/api/queries';
import type { CursorPaginateResponseProblemBookmarkResponseDto, ProblemStatusDto } from './__generated__/dto';
import type {
  TChatsGlobalMutationEffects,
  TGlobalMutationEffectFactory,
  TGoalsGlobalMutationEffects,
} from './__generated__/global-mutation-effect.type';

export const globalMutationEffects: TGlobalMutationEffectFactory = (queryClient) => ({
  ...chatGlobalMutationEffects(queryClient),
  ...goalGlobalMutationEffects(queryClient),
});

export const isGlobalMutationEffectKey = (key: unknown): key is keyof ReturnType<typeof globalMutationEffects> => {
  return typeof key === 'string' && Object.keys(globalMutationEffects(queryClient)).includes(key);
};

function chatGlobalMutationEffects(queryClient: QueryClient): TChatsGlobalMutationEffects {
  return {
    postChatsByChatIdStopConversation: {
      onSuccess: {
        invalidate: (_data, variables) => {
          // 채팅방 목록
          queryClient.invalidateQueries({
            queryKey: chatsQueries.getChatsByChatIdMessages({ chatId: variables.chatId }).queryKey,
            exact: true,
          });
        },
      },
    },
    deleteChatsByChatId: {
      onSuccess: {
        invalidate: (_data, variables) => {
          const { chatId } = variables;

          // 채팅방 상세 정보
          queryClient.removeQueries({
            queryKey: chatsQueries.getChatsByChatId({ chatId }).queryKey,
            exact: true,
          });

          // 채팅방 메시지 목록
          queryClient.removeQueries({
            queryKey: chatsQueries.getChatsByChatIdMessages({ chatId }).queryKey,
            exact: true,
          });

          // 채팅방 문제 목록
          queryClient.removeQueries({
            queryKey: chatsQueries.getChatsByChatIdProblems({ chatId }).queryKey,
            exact: true,
          });

          // 채팅방 스트림 상태
          queryClient.removeQueries({
            queryKey: chatsQueries.getChatsByChatIdStreamStatus({ chatId }).queryKey,
            exact: true,
          });

          // 채팅방 목록
          queryClient.invalidateQueries({
            queryKey: chatsQueryKeys.getChats.rootKey,
          });
        },
      },
    },
    postChatsByChatIdProblemsByProblemIdSubmit: {
      onSuccess: {
        invalidate: (data, variables) => {
          if (data.active_goal && data.is_correct) {
            queryClient.invalidateQueries({
              queryKey: chatsQueries.getChatsByChatId({ chatId: variables.chatId }).queryKey,
              exact: true,
            });
          }

          queryClient.invalidateQueries({
            queryKey: chatsQueries.getChatsByChatIdProblems({ chatId: variables.chatId }).queryKey,
            exact: true,
          });

          queryClient.invalidateQueries({
            queryKey: chatsQueries.getChatsByChatIdProblemsByProblemId({
              chatId: variables.chatId,
              problemId: variables.problemId,
            }).queryKey,
            exact: true,
          });

          queryClient.invalidateQueries({
            queryKey: problemBookmarksQueries.getProblemBookmarksProblemByProblemIdCheck({
              problemId: variables.problemId,
            }).queryKey,
            exact: true,
          });

          /**
           * [북마크 UX 정책]
           * - 북마크 페이지에서 아이템의 북마크 아이콘을 클릭해도 해당 아이템은 즉시 리스트에서 제거되지 않는다.
           * - 실수로 북마크를 해제했을 경우, 다시 아이콘을 눌러 빠르게 실행 취소할 수 있도록 하기 위함이다.
           *
           * [UI 동작 방식]
           * - 북마크 해제 시:
           *   - 리스트에서는 아이템을 유지
           *   - 아이콘만 채워진 북마크 → 빈 북마크로 변경
           *
           * [중요한 구현 제약]
           * - 문제 풀이 완료 후 북마크 상태를 갱신할 때 북마크 리스트 전체를 invalidate 하면 안 된다. (invalidate 시 아이템이 리스트에서 제거되어 UX 정책이 깨짐)
           *
           * [결론]
           * - onSuccess 로직에서는 전체 리스트를 갱신하지 않고 해당 문제의 풀이 상태(status)만 업데이트해야 한다.
           */
          queryClient.setQueriesData<InfiniteData<CursorPaginateResponseProblemBookmarkResponseDto>>(
            { queryKey: problemBookmarksQueryKeys.getProblemBookmarks.rootKey },
            (oldData) => {
              if (!oldData) return oldData;

              return {
                ...oldData,
                pages: oldData.pages.map((page) => ({
                  ...page,
                  items: page.items.map((item) => {
                    if (item.problem.problem_info.id !== variables.problemId) return item;

                    // 정답인 경우: 이전에 오답이었으면 '복습 완료', 아니면 '정답'
                    // 오답인 경우: '오답'
                    const newStatus: ProblemStatusDto = data.is_correct
                      ? item.problem.status === '오답'
                        ? '복습 완료'
                        : '정답'
                      : '오답';

                    return { ...item, problem: { ...item.problem, status: newStatus } };
                  }),
                })),
              };
            },
          );
        },
      },
    },
    patchChatsByChatId: {
      onSuccess: {
        invalidate: (_data, variables) => {
          // 채팅방 상세 정보
          queryClient.invalidateQueries({
            queryKey: chatsQueries.getChatsByChatId({ chatId: variables.chatId }).queryKey,
            exact: true,
          });

          // 채팅방 목록
          queryClient.invalidateQueries({
            queryKey: chatsQueryKeys.getChats.rootKey,
          });
        },
      },
    },
  };
}

function goalGlobalMutationEffects(queryClient: QueryClient): TGoalsGlobalMutationEffects {
  return {
    postGoals: {
      onSuccess: {
        invalidate: (_data, variables) => {
          /**
           * 각 채팅방의 목표 존재 여부에 따라 채팅 목록에서 뱃지를 노출하기 때문에 갱신이 필요함.
           */
          queryClient.invalidateQueries({
            queryKey: chatsQueryKeys.getChats.rootKey,
            exact: true,
          });

          /**
           * 채팅방 상세 정보에 해당 채팅방의 목표 설정 여부가 포함되어 있음.
           * 목표 설정 후 목표 진행률 뱃지를 표시하기 위해 채팅방 상세 정보 갱신이 필요함.
           */
          queryClient.invalidateQueries({
            queryKey: chatsQueries.getChatsByChatId({ chatId: variables.payload.chat_id }).queryKey,
            exact: true,
          });

          /**
           * 목표가 설정되어있는 채팅방에 속한 문제는 북마크 페이지에서 콜아웃을 노출해야 하기 때문에 리스트를 갱신함.
           * 단, 목표 설정 시에는 이 목표가 어떤 과목에 속한 것인지 알 수 없기 때문에 수학, 영어 리스트 둘 다 갱신이 필요
           */
          queryClient.invalidateQueries({
            queryKey: problemBookmarksQueries.getProblemBookmarks({ params: { subject: 'math' } }).queryKey,
          });
          queryClient.invalidateQueries({
            queryKey: problemBookmarksQueries.getProblemBookmarks({ params: { subject: 'english' } }).queryKey,
          });
        },
      },
    },
    deleteGoalsByGoalId: {
      onSuccess: {
        invalidate: () => {
          /**
           * 각 채팅방의 목표 존재 여부에 따라 채팅 목록에서 뱃지를 노출하기 때문에 갱신이 필요함.
           */
          queryClient.invalidateQueries({
            queryKey: chatsQueryKeys.getChats.rootKey,
          });

          /**
           * 채팅방 상세 정보에 해당 채팅방의 목표 설정 여부가 포함되어 있음.
           * 목표 취소 후 목표 진행률 뱃지를 숨기기 위해 채팅방 상세 정보 갱신이 필요함.
           */
          queryClient.invalidateQueries({
            queryKey: chatsQueryKeys.getChatsByChatId.rootKey,
          });

          /**
           * 목표가 설정되어있는 채팅방에 속한 문제는 북마크 페이지에서 콜아웃을 노출해야 하기 때문에 리스트를 갱신함.
           * 단, 목표 설정 시에는 이 목표가 어떤 과목에 속한 것인지 알 수 없기 때문에 수학, 영어 리스트 둘 다 갱신이 필요
           */
          queryClient.invalidateQueries({
            queryKey: problemBookmarksQueries.getProblemBookmarks({ params: { subject: 'math' } }).queryKey,
          });
          queryClient.invalidateQueries({
            queryKey: problemBookmarksQueries.getProblemBookmarks({ params: { subject: 'english' } }).queryKey,
          });
        },
      },
    },
  };
}
