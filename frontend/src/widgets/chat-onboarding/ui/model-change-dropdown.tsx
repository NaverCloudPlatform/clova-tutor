/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Link } from '@tanstack/react-router';
import { CheckIcon, ChevronDownIcon } from 'lucide-react';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/shared/ui/dropdown-menu';

export function ModelChangeDropdown() {
  const { subjectName, isMathSubject, isEnglishSubject } = useSubject();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="group flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-secondary">
        <span className="font-bold text-lg">Clova Tutor</span>
        <span className="text-sm text-foreground-weak">{subjectName} 튜터</span>
        <ChevronDownIcon className="size-5 stroke-foreground-weak transition-transform duration-200 group-data-[state=open]:-rotate-180" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-50">
        <Link from="/$subject/chats" to="/$subject/chats" params={{ subject: 'math' }}>
          <DropdownMenuItem className="flex justify-between items-center">
            <div className="flex flex-col gap-1 items-start">
              <p className="font-semibold text-sm">수학 튜터</p>
              <p className="text-xs text-foreground-weak">즐거운 수학 공부하기</p>
            </div>
            {isMathSubject && <CheckIcon className="size-5" />}
          </DropdownMenuItem>
        </Link>

        <Link from="/$subject/chats" to="/$subject/chats" params={{ subject: 'english' }}>
          <DropdownMenuItem className="flex justify-between items-center">
            <div className="flex flex-col gap-1 items-start">
              <p className="font-semibold text-sm">영어 튜터</p>
              <p className="text-xs text-foreground-weak">재미있는 영어 공부하기</p>
            </div>
            {isEnglishSubject && <CheckIcon className="size-5" />}
          </DropdownMenuItem>
        </Link>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
