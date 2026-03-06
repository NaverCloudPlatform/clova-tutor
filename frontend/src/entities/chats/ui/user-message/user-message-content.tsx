/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { keyBy } from 'es-toolkit';
import { ChevronDownIcon } from 'lucide-react';
import type React from 'react';
import { useRef } from 'react';
import { ChatImages } from '@/entities/chats/ui/chat-images';
import type { ChatMessageResponseDto } from '@/shared/api/__generated__/dto';
import { useIsTextClamped } from '@/shared/hooks/use-is-text-clamped';
import { Button } from '@/shared/ui/button';
import { Collapsible, CollapsibleTrigger } from '@/shared/ui/collapsible';
import { UserMessageQuote } from './user-message-quote';
import { UserMessageText } from './user-message-text';

type UserMessaegContentProps = {
  message: ChatMessageResponseDto;
  userChatBadge: React.ReactElement;
};

export function UserMessaegContent({ message, userChatBadge }: UserMessaegContentProps) {
  const { ref: textRef, isClamped } = useIsTextClamped<HTMLDivElement>();
  const wasClampedRef = useRef(false);
  const contentByMType = keyBy(message.contents, (content) => content.m_type);

  // 한 번이라도 clamped 상태였으면 버튼을 계속 보여줌
  if (isClamped) {
    wasClampedRef.current = true;
  }
  const showToggleButton = wasClampedRef.current || isClamped;

  return (
    <div className="pt-8">
      {contentByMType.images?.m_type === 'images' && (
        <div className="mb-2">
          <ChatImages images={contentByMType.images.value.sources} />
        </div>
      )}
      {contentByMType.quote?.m_type === 'quote' && <UserMessageQuote content={contentByMType.quote} />}
      <Collapsible className="group flex items-start gap-2 bg-secondary text-secondary-foreground px-4 py-2 rounded-lg border w-fit ms-auto">
        <div className="space-y-1 text-start">
          {userChatBadge}

          {contentByMType.text?.m_type === 'text' && (
            <div ref={textRef} className="line-clamp-3 group-data-[state=open]:line-clamp-none">
              <UserMessageText content={contentByMType.text} />
            </div>
          )}
        </div>
        {showToggleButton && (
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-full">
              <ChevronDownIcon className="stroke-muted-foreground group-data-[state=open]:rotate-180" />
            </Button>
          </CollapsibleTrigger>
        )}
      </Collapsible>
    </div>
  );
}
