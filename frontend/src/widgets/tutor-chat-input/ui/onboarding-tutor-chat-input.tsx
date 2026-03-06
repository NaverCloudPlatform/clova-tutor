/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQuery } from '@tanstack/react-query';
import { useRouter } from '@tanstack/react-router';
import { debounce } from 'es-toolkit';
import { usePostChatsMutation } from '@/entities/chats/__generated__/api/mutations';
import { useChatStreamMutation } from '@/entities/chats/hooks/use-chat-stream';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { usersQueries } from '@/entities/users/__generated__/api/queries';
import type { ChatMessageCreateRequestBodyDto } from '@/shared/api/__generated__/dto';
import { TutorChatInputForm } from './tutor-chat-input-form';

export function OnboardingTutorChatInput() {
  const router = useRouter();
  const { subject } = useSubject();
  const { data: user } = useQuery({
    ...usersQueries.getUsersByUserId({
      userId: localStorage.getItem('userId') ?? '',
    }),
  });
  const { mutate: createChat } = usePostChatsMutation();
  const { streamMutate } = useChatStreamMutation({ isCreateChat: true });

  const handleSubmit = debounce((payload: ChatMessageCreateRequestBodyDto) => {
    if (!user) return;

    createChat(
      {
        payload: {
          title: '',
          subject,
          grade: String(user.grade),
        },
      },
      {
        onSuccess: (data) => {
          streamMutate(Number(data.id), payload, {
            message_send: () => {
              router.navigate({
                to: `/${subject}/chats/$chat_id`,
                params: {
                  chat_id: data.id.toString(),
                },
              });
            },
          });
        },
      },
    );
  }, 200);

  return <TutorChatInputForm onSubmit={handleSubmit} />;
}
