/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link } from '@tanstack/react-router';
import { BellRingIcon } from 'lucide-react';
import { toast } from 'sonner';
import type { MessageListResponseDto } from '@/shared/api/__generated__/dto';

let activeToastId: string | number | null = null;

type ChatNotificationToastProps = {
  chatId: number;
  message: MessageListResponseDto['data'][number];
  subject: string;
};

export function chatNotificationToast({ chatId, message: { contents }, subject }: ChatNotificationToastProps) {
  const textContent = contents?.find((item) => item.m_type === 'text')?.value.text;
  const problemRecommended = contents?.find((item) => item.m_type === 'problem_recommended');

  if (!textContent) return;

  if (activeToastId !== null) {
    toast.dismiss(activeToastId);
  }

  const linkTo = problemRecommended?.value.problem_id
    ? {
        to: '/$subject/chats/$chat_id/problem' as const,
        params: {
          subject,
          chat_id: chatId.toString(),
        },
        search: {
          problem_id: problemRecommended.value.problem_id,
        },
      }
    : {
        to: '/$subject/chats/$chat_id' as const,
        params: { subject, chat_id: chatId.toString() },
      };

  const id = toast(
    () => (
      <Link
        to={linkTo.to}
        params={linkTo.params}
        search={linkTo.search}
        onClick={() => {
          toast.dismiss(id);
        }}
      >
        <div className="flex gap-x-2">
          <div className="shrink-0 pt-0.5">
            <BellRingIcon className="w-4 h-4" />
          </div>
          <div className="flex flex-col gap-y-0.5">
            <h6 className="text-sm font-semibold">새로운 메시지가 도착했습니다.</h6>
            <span className="text-xs text-muted-foreground line-clamp-2">{textContent}</span>
          </div>
        </div>
      </Link>
    ),
    {
      position: 'top-right',
      duration: 5000,
      dismissible: true,
    },
  );

  activeToastId = id;
}
