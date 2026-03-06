/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useMatch } from '@tanstack/react-router';
import { FolderClosedIcon, FolderOpenIcon } from 'lucide-react';
import { Suspense } from 'react';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { ApiErrorBoundary } from '@/packages/error-boundary';
import { SUBJECT_NAMES } from '@/shared/constants/subject';
import type { Subject } from '@/shared/types/common';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/shared/ui/collapsible';
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarMenuSub } from '@/shared/ui/sidebar';
import { ChatList, ChatListSkeleton } from './chat-list';

type Props = {
  subject: Subject;
};

export function ChatSidebarSubjectSection({ subject }: Props) {
  const { subject: currentSubject } = useSubject();
  const isOnboardingPage = useMatch({
    from: '/_student/$subject/',
    shouldThrow: false,
  });

  return (
    <SidebarMenu>
      <Collapsible className="group/collapsible" defaultOpen={!isOnboardingPage && currentSubject === subject} asChild>
        <SidebarMenuItem>
          <CollapsibleTrigger asChild>
            <SidebarMenuButton>
              <FolderClosedIcon className="block group-data-[state=open]/collapsible:hidden" />
              <FolderOpenIcon className="hidden group-data-[state=open]/collapsible:block" />
              <span>{SUBJECT_NAMES[subject]} 채팅</span>
            </SidebarMenuButton>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <SidebarMenuSub className="mr-0 pr-0" aria-label={`최근 ${SUBJECT_NAMES[subject]} 채팅 기록`}>
              <ApiErrorBoundary>
                <Suspense fallback={<ChatListSkeleton />}>
                  <ChatList subject={subject} />
                </Suspense>
              </ApiErrorBoundary>
            </SidebarMenuSub>
          </CollapsibleContent>
        </SidebarMenuItem>
      </Collapsible>
    </SidebarMenu>
  );
}
