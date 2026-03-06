/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useShallow } from 'zustand/shallow';
import { useChatInputMapKey } from '@/entities/chats/hooks/use-chat-input-map-key';
import { useChatStore } from '@/entities/chats/store/chats';
import { useChatFileStore } from '../store/chat-file';
import type { UploadedFileData } from '../types/file';

export function useChatFile() {
  const inputMapId = useChatInputMapKey();
  const pendingFiles = useChatFileStore(useShallow((state) => state.getFiles(inputMapId)));
  const uploadedFiles = useChatStore(
    useShallow(
      (state) => state.getChatInput(inputMapId)?.find((content) => content.m_type === 'images')?.value.sources,
    ),
  );

  const convertUploadedFilesToFileData = (uploadedFiles: string[]) => {
    return uploadedFiles.map((url) => ({
      url,
      status: 'uploaded',
    })) as UploadedFileData[];
  };

  const files = [...pendingFiles, ...convertUploadedFilesToFileData(uploadedFiles ?? [])];

  return {
    files,
  };
}
