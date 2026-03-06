/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { unionWith } from 'es-toolkit';
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { ChatMessageResponseDto, SubjectEnumDto } from '@/shared/api/__generated__/dto';
import { LOCAL_STORAGE_KEY } from '@/shared/constants/storage-key';

type InputState = {
  inputMap: Record<string, ChatMessageResponseDto['contents']>;
  saveChatInput: (chatId: number | SubjectEnumDto, contents: ChatMessageResponseDto['contents']) => void;
  upsertChatContent: (chatId: number | SubjectEnumDto, contents: ChatMessageResponseDto['contents']) => void;
  removeChatContent: (chatId: number | SubjectEnumDto, mType: string) => void;
  removeEmptyContent: (chatId: number | SubjectEnumDto, options?: { keepTypes?: string[] }) => void;
  removeChatInput: (chatId: number | SubjectEnumDto) => void;
  removeEmptyChatInput: (chatId: number | SubjectEnumDto) => void;
  getChatInput: (chatId: number | SubjectEnumDto) => ChatMessageResponseDto['contents'] | undefined;
  hasChatInput: (chatId: number | SubjectEnumDto) => boolean;
};

export const useChatStore = create<InputState>()(
  devtools(
    persist(
      (set, get) => ({
        inputMap: {} as Record<string, ChatMessageResponseDto['contents']>,

        saveChatInput: (chatId, contents) => {
          set(
            (state) => ({
              inputMap: {
                ...state.inputMap,
                [String(chatId)]: contents,
              },
            }),
            false,
            'saveChatInput',
          );
        },
        upsertChatContent: (chatId, contents) => {
          set(
            (state) => ({
              inputMap: {
                ...state.inputMap,
                [String(chatId)]: unionWith(
                  contents,
                  state.inputMap[String(chatId)] || [],
                  (a, b) => a.m_type === b.m_type,
                ),
              },
            }),
            false,
            'upsertChatContent',
          );
        },
        removeChatContent: (chatId, mType) => {
          set(
            (state) => ({
              inputMap: {
                ...state.inputMap,
                [String(chatId)]: state.inputMap[String(chatId)]?.filter((content) => content.m_type !== mType),
              },
            }),
            false,
            'removeChatContent',
          );
        },
        removeEmptyContent: (chatId, options) => {
          set(
            (state) => ({
              inputMap: {
                ...state.inputMap,
                [String(chatId)]: state.inputMap[String(chatId)]?.filter((content) => {
                  // keepTypes에 포함된 타입은 유지
                  if (options?.keepTypes?.includes(content.m_type)) {
                    return true;
                  }

                  if (content.m_type === 'text' || content.m_type === 'quote') {
                    return content.value.text.trim() !== '';
                  }
                  if (content.m_type === 'images') {
                    return content.value.sources.length > 0;
                  }
                  if (content.m_type === 'problem_link') {
                    return false;
                  }

                  return true;
                }),
              },
            }),
            false,
            'removeEmptyContent',
          );
        },
        removeChatInput: (chatId) => {
          set(
            (state) => {
              const newMap = { ...state.inputMap };
              delete newMap[String(chatId)];
              return { inputMap: newMap };
            },
            false,
            'removeChatInput',
          );
        },
        removeEmptyChatInput: (chatId) => {
          set(
            (state) => {
              const contents = state.inputMap[String(chatId)];

              if (!contents || contents.length === 0) {
                const newMap = { ...state.inputMap };
                delete newMap[String(chatId)];
                return { inputMap: newMap };
              }

              return state;
            },
            false,
            'removeEmptyChatInput',
          );
        },
        getChatInput: (chatId) => get().inputMap[String(chatId)],
        hasChatInput: (chatId) => String(chatId) in get().inputMap,
      }),
      {
        name: LOCAL_STORAGE_KEY.CHAT_INPUT_STORE,
        partialize: (state) => ({ inputMap: state.inputMap }),
        version: 1,
        migrate: (persistedState: unknown, version: number) => {
          if (version !== 0) return persistedState;
          if (typeof persistedState !== 'object' || persistedState === null) return persistedState;

          if ('inputMap' in persistedState && persistedState?.inputMap) {
            const migratedInputMap: Record<string, ChatMessageResponseDto['contents']> = {};

            for (const [chatId, value] of Object.entries(persistedState.inputMap)) {
              const text = typeof value === 'string' && value.trim() ? value.trim() : null;
              if (!text) continue;

              migratedInputMap[chatId] = [
                {
                  m_type: 'text',
                  value: { text },
                },
              ];
            }

            return { inputMap: migratedInputMap };
          }

          return persistedState;
        },
      },
    ),
    { name: 'ChatStore', enabled: import.meta.env.DEV },
  ),
);
