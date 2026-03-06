/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { ChatProblemResponseDto } from '@/shared/api/__generated__/dto';
import { SESSION_STORAGE_KEY } from '@/shared/constants/storage-key';

type ProblemData = {
  lastProblemId: ChatProblemResponseDto['id'] | null;
};

type ProblemState = {
  problemsByChat: Record<number, ProblemData>;
  setLastProblemId: (chatId: number, id: ChatProblemResponseDto['id'] | null) => void;
  resetLastProblemId: (chatId: number) => void;
  getLastProblemId: (chatId: number) => ChatProblemResponseDto['id'] | null;
};

export const useProblemStore = create<ProblemState>()(
  devtools(
    persist(
      (set, get) => ({
        problemsByChat: {},

        setLastProblemId: (chatId, id) =>
          set(
            (state) => ({
              problemsByChat: {
                ...state.problemsByChat,
                [chatId]: {
                  ...state.problemsByChat[chatId],
                  lastProblemId: id,
                },
              },
            }),
            false,
            'setLastProblemId',
          ),

        resetLastProblemId: (chatId) => {
          set(
            (state) => ({
              problemsByChat: {
                ...state.problemsByChat,
                [chatId]: {
                  ...state.problemsByChat[chatId],
                  lastProblemId: null,
                },
              },
            }),
            false,
            'resetLastProblemId',
          );
        },

        getLastProblemId: (chatId) => {
          return get().problemsByChat[chatId]?.lastProblemId ?? null;
        },
      }),
      {
        name: SESSION_STORAGE_KEY.PROBLEM_STORE,
        storage: {
          getItem: (name) => {
            let value = sessionStorage.getItem(name);

            if (!value) {
              const localValue = localStorage.getItem(name);
              if (localValue) {
                try {
                  sessionStorage.setItem(name, localValue);
                  localStorage.removeItem(name);
                  value = localValue;
                  console.log('[ProblemStore] Migrated from localStorage to sessionStorage');
                } catch (error) {
                  console.error('[ProblemStore] Failed to migrate to sessionStorage:', error);
                }
              }
            }

            return value ? JSON.parse(value) : null;
          },
          setItem: (name, value) => {
            sessionStorage.setItem(name, JSON.stringify(value));
          },
          removeItem: (name) => {
            sessionStorage.removeItem(name);
          },
        },
        partialize: (state) => ({
          problemsByChat: state.problemsByChat,
        }),
        version: 1,
        migrate: (persistedState: unknown, version: number) => {
          // version 0 -> 1: problem_id가 number에서 string으로 변경됨
          if (version === 0) {
            if (typeof persistedState !== 'object' || persistedState === null) return persistedState;

            if ('problemsByChat' in persistedState && persistedState.problemsByChat) {
              const migratedProblems: Record<number, ProblemData> = {};

              for (const [chatId, data] of Object.entries(persistedState.problemsByChat as Record<string, unknown>)) {
                if (data && typeof data === 'object' && 'lastProblemId' in data) {
                  const lastProblemId = (data as { lastProblemId: unknown }).lastProblemId;
                  migratedProblems[Number(chatId)] = {
                    // number를 string으로 변환, 이미 string이면 그대로 유지
                    lastProblemId: lastProblemId != null ? String(lastProblemId) : null,
                  };
                }
              }

              return { problemsByChat: migratedProblems };
            }
          }

          return persistedState;
        },
      },
    ),
    { name: 'ProblemStore', enabled: import.meta.env.DEV },
  ),
);
