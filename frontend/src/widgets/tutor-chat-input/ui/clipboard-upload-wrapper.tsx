/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ClipboardEvent } from 'react';
import { useChatFileUpload } from '@/features/chat-file-upload/hook/use-chat-file-upload';

type Props = {
  children: React.ReactNode;
};

export function ClipboardUploadWrapper({ children }: Props) {
  const { addFiles } = useChatFileUpload({});

  const handlePaste = (e: ClipboardEvent<HTMLDivElement>) => {
    const file = e.clipboardData.files[0];

    if (!file || !['image/jpeg', 'image/png'].includes(file.type)) return;

    e.preventDefault();

    addFiles([file]);
  };

  return <div onPaste={handlePaste}>{children}</div>;
}
