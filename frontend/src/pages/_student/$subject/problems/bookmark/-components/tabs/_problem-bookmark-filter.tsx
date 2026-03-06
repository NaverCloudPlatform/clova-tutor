/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useNavigate, useSearch } from '@tanstack/react-router';
import { ChevronDownIcon, FilterIcon } from 'lucide-react';
import { ProblemStatusBadge } from '@/entities/problems/ui/problem-status-badge';
import type { ProblemStatusDto } from '@/shared/api/__generated__/dto';
import { Button } from '@/shared/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu';

const STATUS_OPTIONS = [
  { value: '복습 완료', label: '복습 완료' },
  { value: '오답', label: '오답' },
  { value: '정답', label: '정답' },
  { value: '풀지 않음', label: '풀지 않음' },
] as const;

export function ProblemBookmarkStatusFilter() {
  const navigate = useNavigate();
  const search = useSearch({ from: '/_student/$subject/problems/bookmark/' });
  const selectedStatuses = search.status || [];

  const handleStatusToggle = (status: ProblemStatusDto) => {
    const newStatuses = selectedStatuses.includes(status)
      ? selectedStatuses.filter((s) => s !== status)
      : [...selectedStatuses, status];

    navigate({
      to: '.',
      search: {
        status: newStatuses,
      },
    });
  };

  return (
    <DropdownMenu modal>
      <DropdownMenuTrigger className="group" asChild>
        <Button variant="outline" size="sm">
          <FilterIcon className="size-4" />
          필터
          <ChevronDownIcon className="size-4 ml-1 group-data-[state=open]:-rotate-180 transition-transform duration-100" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="text-xs text-muted-foreground pb-2">문제 상태</DropdownMenuLabel>

        {STATUS_OPTIONS.map((option) => (
          <DropdownMenuCheckboxItem
            key={option.value}
            checked={selectedStatuses.includes(option.value)}
            onCheckedChange={() => handleStatusToggle(option.value)}
            onSelect={(e) => e.preventDefault()}
          >
            <ProblemStatusBadge status={option.value} />
            {option.label}
          </DropdownMenuCheckboxItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
