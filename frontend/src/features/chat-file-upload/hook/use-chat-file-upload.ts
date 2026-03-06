/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { compact } from 'es-toolkit';
import { useShallow } from 'zustand/shallow';
import { useChatInputMapKey } from '@/entities/chats/hooks/use-chat-input-map-key';
import { useChatStore } from '@/entities/chats/store/chats';
import { useNcpStorage } from '@/entities/upload/hook/use-ncp-storage';
import { processImageFile } from '@/entities/upload/utils/image-validation';
import { useChatFileStore } from '../store/chat-file';

type UseChatFileUploadParams = {
  maxFiles?: number;
};

export function useChatFileUpload({ maxFiles = 1 }: UseChatFileUploadParams) {
  const inputMapKey = useChatInputMapKey();
  const { uploadFile: uploadToStorage } = useNcpStorage();
  const { addFile, updateFileStatus, removeFile, clearFiles, getFiles } = useChatFileStore(
    useShallow((state) => ({
      addFile: state.addFile,
      updateFileStatus: state.updateFileStatus,
      removeFile: state.removeFile,
      clearFiles: state.clearFiles,
      getFiles: state.getFiles,
    })),
  );
  const upsertChatContent = useChatStore((state) => state.upsertChatContent);

  const files = getFiles(inputMapKey);

  const uploadSingleFile = async (file: File) => {
    const fileData = {
      file,
      previewUrl: URL.createObjectURL(file),
      status: 'uploading' as const,
    };

    addFile(inputMapKey, fileData);

    uploadToStorage(file, {
      onSuccess: (url) => {
        upsertChatContent(inputMapKey, [
          {
            m_type: 'images',
            value: { sources: [url] },
          },
        ]);

        removeFile(inputMapKey, file.name);
      },
      onError: () => {
        updateFileStatus(inputMapKey, file.name, 'failed');
      },
    });
  };

  const addFiles = async (newFiles: File[]) => {
    const processedFiles = compact(await Promise.all(newFiles.map(processImageFile)));

    if (processedFiles.length === 0) return;

    const currentCount = files.length;
    const filesToUpload = processedFiles.slice(0, maxFiles - currentCount);

    filesToUpload.forEach(uploadSingleFile);
  };

  const retryUpload = (fileName: string) => {
    const fileData = files.find((f) => f.file?.name === fileName);
    if (!fileData || !fileData.file) return;

    updateFileStatus(inputMapKey, fileName, 'uploading');
    uploadSingleFile(fileData.file);
  };

  const removeFileByName = (fileName: string) => {
    removeFile(inputMapKey, fileName);
  };

  const clearAllFiles = () => {
    clearFiles(inputMapKey);
  };

  return {
    files,
    addFiles,
    retryUpload,
    removeFile: removeFileByName,
    clearAllFiles,
  };
}
