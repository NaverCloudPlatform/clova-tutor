/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { debounce } from 'es-toolkit';
import { useState } from 'react';
import { toast } from 'sonner';
import { usePatchChatsByChatIdMutation } from '@/entities/chats/__generated__/api/mutations';
import { Input } from '@/shared/ui/input';
import { cn } from '@/shared/utils/utils';

const MAX_TITLE_LENGTH = 100;

type Props = {
  chatId: number;
  initialTitle: string;
  onBlur: () => void;
  classNames?: {
    input?: string;
  };
} & React.ComponentProps<'div'>;

export function ChatTitleEdit({ chatId, initialTitle, onBlur, classNames, ...props }: Props) {
  const { mutate: updateChatTitle } = usePatchChatsByChatIdMutation({});
  const [title, setTitle] = useState(initialTitle);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  const handleBlur = debounce(() => {
    if (title.trim() === initialTitle.trim()) {
      return;
    }

    const trimmedTitle = title.trim();
    if (trimmedTitle.length === 0) {
      toast.error('채팅 제목을 입력해주세요.');
      setTitle(initialTitle);
      return;
    }

    if (trimmedTitle !== initialTitle && trimmedTitle.length <= MAX_TITLE_LENGTH) {
      updateChatTitle({
        chatId,
        payload: { title: trimmedTitle },
      });
    }
  }, 50);

  return (
    <div {...props}>
      <Input
        className={cn('border-none shadow-none h-full', classNames?.input)}
        ref={(ref) => {
          if (ref && !ref.dataset.initialized) {
            ref.focus();
            ref.select();
            ref.scrollLeft = 0;
            ref.dataset.initialized = 'true';
          }
        }}
        value={title}
        onChange={(e) => {
          const newValue = e.target.value;
          if (newValue.length > MAX_TITLE_LENGTH) {
            toast.error(`채팅 제목은 ${MAX_TITLE_LENGTH}자 이하로 입력해주세요.`);
            return;
          }
          setTitle(newValue);
        }}
        onKeyDown={handleKeyDown}
        onBlur={() => {
          onBlur();
          handleBlur();
        }}
        placeholder="채팅 제목을 입력하세요"
      />
    </div>
  );
}
