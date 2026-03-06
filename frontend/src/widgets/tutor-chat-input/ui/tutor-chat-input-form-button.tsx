/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { debounce } from 'es-toolkit';
import { SendIcon, SquareIcon } from 'lucide-react';
import { useShallow } from 'zustand/shallow';
import { usePostChatsByChatIdStopConversationMutation } from '@/entities/chats/__generated__/api/mutations';
import { useChatInputMapKey } from '@/entities/chats/hooks/use-chat-input-map-key';
import { useChatStreamAbort } from '@/entities/chats/hooks/use-chat-stream-abort';
import { useChatStreamMutationState } from '@/entities/chats/hooks/use-chat-stream-mutation-state';
import { useChatFileStore } from '@/features/chat-file-upload/store/chat-file';
import { useRichEditorStore } from '@/packages/rich-editor/store/use-rich-editor-store';
import { Button } from '@/shared/ui/button';

export function TutorChatInputFormButton() {
  const { chat_id: chatId } = useParams({
    strict: false,
  });
  const { isStreaming } = useChatStreamMutationState({
    chatId: Number(chatId),
  });

  if (!chatId || !isStreaming) return <SubmitChatStreamButton />;

  return <AbortChatStreamButton />;
}

function AbortChatStreamButton() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });

  const { mutate: stopChatStream } = usePostChatsByChatIdStopConversationMutation();
  const { abortChatStream } = useChatStreamAbort({
    chatId: Number(chatId),
  });

  const handleAbortChatStream = debounce(() => {
    stopChatStream(
      { chatId: Number(chatId) },
      {
        onSuccess: () => {
          abortChatStream();
        },
      },
    );
  }, 500);

  return (
    <Button
      type="button"
      size="icon"
      variant="ghost"
      className="bg-accent-blue-100 hover:bg-accent-blue-100 text-foreground"
      aria-label="채팅 중단"
      onClick={handleAbortChatStream}
    >
      <SquareIcon className="size-3 fill-foreground" />
    </Button>
  );
}

function SubmitChatStreamButton() {
  const inputMapKey = useChatInputMapKey();
  const { isPendingFileExists } = useChatFileStore(
    useShallow((state) => ({
      isPendingFileExists: state.getFiles(inputMapKey).length > 0,
    })),
  );
  const isEmpty = useRichEditorStore((state) => state.isEmpty);

  return (
    <Button type="submit" size="icon" disabled={isEmpty || isPendingFileExists} aria-label="채팅 전송">
      <SendIcon />
    </Button>
  );
}
