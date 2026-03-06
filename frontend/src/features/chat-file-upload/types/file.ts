/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export type FileStatus = 'uploading' | 'failed' | 'uploaded';

export type FileData = {
  file?: File;
  url?: string;
  previewUrl?: string;
  status: FileStatus;
};

export type PendingFileData = {
  file: File;
  previewUrl?: string;
  status: Exclude<FileStatus, 'uploaded'>;
};

export type UploadedFileData = {
  url: string;
  status: Extract<FileStatus, 'uploaded'>;
};
