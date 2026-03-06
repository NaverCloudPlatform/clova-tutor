/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { MonitorIcon, MoonIcon, PaletteIcon, SunIcon } from 'lucide-react';
import { useTheme } from '@/app/provider/theme-provider';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/shared/ui/dropdown-menu';
import { cn } from '@/shared/utils/utils';

export function ThemeChangeDropdown() {
  const { theme, setTheme } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <DropdownMenuItem className="w-full">
          <PaletteIcon className="size-4" />
          테마
        </DropdownMenuItem>
      </DropdownMenuTrigger>
      <DropdownMenuContent side="right" align="start" sideOffset={16} className="space-y-0.5">
        <DropdownMenuItem className={cn(theme === 'system' && 'bg-accent')} onClick={() => setTheme('system')}>
          <MonitorIcon className="size-4" />
          시스템
        </DropdownMenuItem>

        <DropdownMenuItem className={cn(theme === 'light' && 'bg-accent')} onClick={() => setTheme('light')}>
          <SunIcon className="size-4" />
          라이트
        </DropdownMenuItem>

        <DropdownMenuItem className={cn(theme === 'dark' && 'bg-accent')} onClick={() => setTheme('dark')}>
          <MoonIcon className="size-4" />
          다크
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
