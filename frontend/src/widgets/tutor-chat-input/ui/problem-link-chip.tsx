/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useParams } from '@tanstack/react-router';
import { XIcon } from 'lucide-react';
import { useChatStore } from '@/entities/chats/store/chats';
import { Button } from '@/shared/ui/button';

export function ProblemLinkChip() {
  const { chat_id: chatId } = useParams({
    strict: false,
  });
  const selectedProblemId = useChatStore(
    (state) =>
      state.getChatInput(Number(chatId))?.find((content) => content.m_type === 'problem_link')?.value.problem_id,
  );

  if (!selectedProblemId) return null;

  return <ProblemLinkChipContent />;
}

function ProblemLinkChipContent() {
  const { chat_id: chatId } = useParams({
    from: '/_student/$subject/chats/$chat_id',
  });
  const removeChatContent = useChatStore((state) => state.removeChatContent);

  const handleXButtonClick = () => {
    removeChatContent(Number(chatId), 'problem_link');
  };

  return (
    <Button
      variant="outline"
      size="sm"
      className="group ai-text flex items-center gap-x-1.5 rounded-full"
      onClick={handleXButtonClick}
    >
      {/* 데스크톱: 링크 ↔ 호버 시 X 같은 자리에서 교체 */}
      <span className="relative inline-flex size-4 shrink-0 items-center justify-center">
        <img src="/icons/ai-link.svg" alt="AI 문제 링크" className="size-4 lg:group-hover:hidden" />
        <span className="ai-icon-gradient absolute hidden size-4 lg:group-hover:inline-flex">
          <XIcon className="size-4" />
        </span>
      </span>
      <span>문제 질문중</span>
      {/* 모바일 전용: 오른쪽에 X 항상 노출 */}
      <span className="ai-icon-gradient inline-flex size-4 shrink-0 lg:hidden">
        <XIcon className="size-4" />
      </span>
    </Button>
  );
}
