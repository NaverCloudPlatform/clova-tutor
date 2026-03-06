/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ImagePlusIcon } from 'lucide-react';
import { useRef } from 'react';
import { useChatFile } from '@/features/chat-file-upload/hook/use-chat-file';
import { useChatFileUpload } from '@/features/chat-file-upload/hook/use-chat-file-upload';
import { Button } from '@/shared/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/shared/ui/tooltip';

export function FileUploadButton() {
  const { files } = useChatFile();
  const { addFiles } = useChatFileUpload({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;

    e.target.blur();

    if (selectedFiles && selectedFiles.length > 0) {
      addFiles(Array.from(selectedFiles));

      if (document.activeElement instanceof HTMLElement) {
        document.activeElement.blur();
      }
    }
  };

  return (
    <>
      <input
        type="file"
        accept=".jpeg,.png,.jpg"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
        disabled={files.length > 0}
      />
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="icon"
            aria-label="이미지 업로드"
            disabled={files.length > 0}
            onClick={handleButtonClick}
          >
            <ImagePlusIcon className="size-5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>이미지는 1개씩 올릴 수 있어요</p>
        </TooltipContent>
      </Tooltip>
    </>
  );
}
