/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { MathPortalInfo } from '@/packages/rich-editor/types/math-node';
import { log } from './log';

/**
 * @description
 * 이벤트 이름 형식: {fsd slice name}:{event name}
 */
type EventMap =
  | ({
      type: 'rich-editor:math-node-click';
    } & { callback: (data: MathPortalInfo) => void })
  | ({
      type: 'confetti-container';
    } & { callback: () => void });

type CallbackFor<T extends EventMap['type']> = Extract<EventMap, { type: T }>['callback'];

export const eventManager = (() => {
  const listeners: Record<string, Set<(...args: unknown[]) => void>> = {};

  return {
    on<T extends EventMap['type']>(event: T, listener: CallbackFor<T>) {
      log.debug('eventManager', {
        type: 'on',
        event,
        listener,
      });
      listeners[event] = listeners[event] || new Set();
      listeners[event]?.add(listener as (...args: unknown[]) => void);
    },
    off<T extends EventMap['type']>(event: T, listener: CallbackFor<T>) {
      log.debug('eventManager', {
        type: 'off',
        event,
        listener,
      });
      listeners[event]?.delete(listener as (...args: unknown[]) => void);
    },
    emit<T extends EventMap['type']>(event: T, ...args: Parameters<CallbackFor<T>>) {
      log.debug('eventManager', {
        type: 'emit',
        event,
        args,
      });
      listeners[event]?.forEach((fn) => {
        fn(...args);
      });
    },
  };
})();
