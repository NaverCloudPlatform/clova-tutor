/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { SubjectEnumDto } from '@/shared/api/__generated__/dto';
import type { PendingFileData } from '../types/file';

type FileStoreState = {
  files: Map<number | SubjectEnumDto, PendingFileData[]>;
  addFile: (chatId: number | SubjectEnumDto, fileData: PendingFileData) => void;
  updateFileStatus: (chatId: number | SubjectEnumDto, fileName: string, status: 'uploading' | 'failed') => void;
  removeFile: (chatId: number | SubjectEnumDto, fileName: string) => void;
  clearFiles: (chatId: number | SubjectEnumDto) => void;
  getFiles: (chatId: number | SubjectEnumDto) => PendingFileData[];
};

export const useChatFileStore = create<FileStoreState>()(
  devtools(
    (set, get) => ({
      files: new Map(),

      addFile: (chatId, fileData) => {
        const current = get().files.get(chatId) || [];
        const newFiles = new Map(get().files);
        newFiles.set(chatId, [...current, fileData]);
        set({ files: newFiles }, false, 'addFile');
      },
      updateFileStatus: (chatId, fileName, status) => {
        const current = get().files.get(chatId) || [];
        const newFiles = new Map(get().files);
        newFiles.set(
          chatId,
          current.map((f) => (f.file?.name === fileName ? { ...f, status } : f)),
        );
        set({ files: newFiles }, false, 'updateFileStatus');
      },
      removeFile: (chatId, fileName) => {
        const current = get().files.get(chatId) || [];
        const fileToRemove = current.find((f) => f.file?.name === fileName);

        if (fileToRemove?.previewUrl) {
          URL.revokeObjectURL(fileToRemove.previewUrl);
        }

        const newFiles = new Map(get().files);
        newFiles.set(
          chatId,
          current.filter((f) => f.file?.name !== fileName),
        );
        set({ files: newFiles }, false, 'removeFile');
      },
      clearFiles: (chatId) => {
        const current = get().files.get(chatId) || [];

        current.forEach((f) => {
          if (f.previewUrl) {
            URL.revokeObjectURL(f.previewUrl);
          }
        });

        const newFiles = new Map(get().files);
        newFiles.delete(chatId);
        set({ files: newFiles });
      },
      getFiles: (chatId) => {
        return get().files.get(chatId) || [];
      },
    }),
    { name: 'ChatFileStore', enabled: import.meta.env.DEV },
  ),
);
