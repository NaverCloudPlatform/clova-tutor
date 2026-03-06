/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link } from '@tanstack/react-router';
import { BookmarkIcon, EditIcon } from 'lucide-react';
import { SUBJECT_NAMES } from '@/shared/constants/subject';
import type { Subject } from '@/shared/types/common';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from '@/shared/ui/sidebar';
import { cn } from '@/shared/utils/utils';
import { ChatOptionsMenus } from './chat-options-menus';
import { ChatSidebarSubjectSection } from './chst-sidebar-subject-section';

export function ChatSidebar() {
  const { open, openMobile } = useSidebar();

  return (
    <Sidebar variant="inset" collapsible="icon" className="bg-sidebar select-none">
      <SidebarHeader className="flex flex-row items-center justify-between h-13">
        <SidebarMenu className="group/sidebar-header flex flex-row items-center w-fit">
          <SidebarMenuItem>
            <Link
              to="/$subject"
              params={{ subject: 'math' }}
              className={cn('w-fit', !open && 'md:group-hover/sidebar-header:hidden')}
            >
              <SidebarMenuButton size="lg" className="h-fit p-1">
                <div className={cn('flex aspect-square size-6 items-center justify-center rounded-lg flex-1')}>
                  <img width={24} height={24} src="/math-logo.svg" alt="logo" />
                </div>
              </SidebarMenuButton>
            </Link>

            {!open && <SidebarTrigger className="hidden md:group-hover/sidebar-header:flex" />}
          </SidebarMenuItem>
        </SidebarMenu>

        {(open || openMobile) && <SidebarTrigger />}
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            <SidebarMenuItem>
              <Link from="/$subject" to="/$subject/chats">
                <SidebarMenuButton>
                  <EditIcon className="size-4!" /> <span>새 채팅</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <Link from="/$subject" to="/$subject/problems/bookmark">
                <SidebarMenuButton>
                  <BookmarkIcon className="size-4!" /> <span>학습 노트</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>

        {(open || openMobile) && (
          <SidebarGroup>
            <SidebarGroupLabel>최근 채팅</SidebarGroupLabel>
            {Object.keys(SUBJECT_NAMES).map((subject) => (
              <ChatSidebarSubjectSection key={subject} subject={subject as Subject} />
            ))}
          </SidebarGroup>
        )}
      </SidebarContent>

      <SidebarFooter className="flex justify-between flex-row items-center">
        <ChatOptionsMenus />
      </SidebarFooter>
    </Sidebar>
  );
}
