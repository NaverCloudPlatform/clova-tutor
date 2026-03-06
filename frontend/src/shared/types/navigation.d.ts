/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export interface NavigationEvent extends Event {
  readonly navigationType: 'reload' | 'push' | 'replace' | 'traverse';
  readonly destination: { url: string };
  readonly canIntercept: boolean;
  intercept: (options: { handler: () => Promise<void> }) => void;
}

export interface Navigation {
  addEventListener(type: 'navigate', callback: (event: NavigationEvent) => void): void;
  removeEventListener(type: 'navigate', callback: (event: NavigationEvent) => void): void;
  navigate(url: string, options?: { history?: 'replace' | 'push' }): void;
}