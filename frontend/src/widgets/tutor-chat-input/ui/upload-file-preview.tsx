/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { FileTextIcon, Loader2Icon, RefreshCcwIcon, XIcon } from 'lucide-react';
import { match } from 'ts-pattern';
import { useChatInputMapKey } from '@/entities/chats/hooks/use-chat-input-map-key';
import { useChatStore } from '@/entities/chats/store/chats';
import { useChatFile } from '@/features/chat-file-upload/hook/use-chat-file';
import { useChatFileUpload } from '@/features/chat-file-upload/hook/use-chat-file-upload';
import { Button } from '@/shared/ui/button';
import { cn } from '@/shared/utils/utils';

export function UploadFilePreview() {
  const chatInputMapKey = useChatInputMapKey();
  const removeChatContent = useChatStore((state) => state.removeChatContent);
  const { files } = useChatFile();
  const { retryUpload, removeFile } = useChatFileUpload({});

  if (files.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {files.map((file) =>
        match(file)
          .with({ status: 'uploading' }, ({ file, previewUrl }) => (
            <UploadFilePreviewItem
              key={file.name}
              classNames={{
                removeButton: 'hidden',
              }}
              imageUrl={previewUrl}
              overlayContent={<Loader2Icon className="h-6 w-6 animate-spin text-gray-400" />}
              onRemove={() => removeFile(file.name)}
            />
          ))
          .with({ status: 'uploaded' }, ({ url }) => (
            <UploadFilePreviewItem
              key={url}
              imageUrl={url}
              onRemove={() => removeChatContent(chatInputMapKey, 'images')}
            />
          ))
          .with({ status: 'failed' }, ({ file, previewUrl }) => (
            <UploadFilePreviewItem
              key={file.name}
              imageUrl={previewUrl}
              overlayContent={
                <Button aria-label="이미지 업로드 재시도" variant="ghost" size="icon">
                  <RefreshCcwIcon className="h-6 w-6 text-gray-400" onClick={() => retryUpload(file.name)} />
                </Button>
              }
              onRemove={() => removeFile(file.name)}
            />
          ))
          .otherwise(() => null),
      )}
    </div>
  );
}

type UploadFilePreviewItemProps = {
  classNames?: {
    removeButton?: string;
  };
  imageUrl?: string;
  overlayContent?: React.ReactNode;
  onRemove: () => void;
};

export function UploadFilePreviewItem({ classNames, imageUrl, overlayContent, onRemove }: UploadFilePreviewItemProps) {
  return (
    <div className={cn('relative border rounded-md p-1 w-24 h-24 flex flex-col items-center justify-center')}>
      {overlayContent && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/40 z-10 rounded-md">
          {overlayContent}
        </div>
      )}

      <Button
        type="button"
        variant="ghost"
        size="icon"
        className={cn(
          'absolute top-0.5 right-0.5  h-6 w-6 cursor-pointer bg-transparent z-10',
          classNames?.removeButton,
        )}
        onClick={onRemove}
      >
        <XIcon className={cn('h-3 w-3')} aria-label="첨부된 이미지 삭제" />
      </Button>

      {imageUrl ? (
        <div className="relative w-full h-16 flex items-center justify-center">
          <img src={imageUrl} alt="업로드한 이미지" className="max-w-full max-h-full object-contain" />
        </div>
      ) : (
        <>
          <div className="w-full h-16 flex items-center justify-center">
            <FileTextIcon className="h-10 w-10 text-gray-400" />
          </div>
          <div className="text-xs mt-1 text-center w-full truncate">업로드한 이미지</div>
        </>
      )}
    </div>
  );
}
