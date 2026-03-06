/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import 'mathlive';
import type { MathfieldElement } from 'mathlive';
import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import { cn } from '../utils/utils';

import '@/packages/rich-editor/styles/mathlive.css';
import '@/packages/rich-editor/styles/virturl-keyboard.css';
import { KeyboardIcon } from 'lucide-react';
import { Toggle } from './toggle';

type Props = React.DetailedHTMLProps<React.HTMLAttributes<MathfieldElement>, MathfieldElement> & {
  classNames?: {
    container?: string;
    mathField?: string;
    toggleButton?: string;
  };
};

export const MathLive = forwardRef<MathfieldElement, Props>(({ children, className, classNames, ...props }, ref) => {
  const mathFieldRef = useRef<MathfieldElement>(null);

  useImperativeHandle(ref, () => mathFieldRef.current as MathfieldElement);

  // 가상 키보드 토글 함수
  const toggleVirtualKeyboard = () => {
    if (!window.mathVirtualKeyboard) return;

    if (window.mathVirtualKeyboard.visible) {
      window.mathVirtualKeyboard.hide();
    } else {
      window.mathVirtualKeyboard.show();
      mathFieldRef.current?.focus();
    }
  };

  useEffect(() => {
    const mathField = mathFieldRef.current;
    if (!mathField || typeof window === 'undefined' || !window.mathVirtualKeyboard) return;

    // 1. 초기 설정
    mathField.menuItems = [];

    // 3. 줄바꿈 방지: 기본 동작만 막고, 전파는 허용하여 상위(예: math-popover)에서 엔터로 닫기 등 처리 가능하게 함
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        // stopPropagation 하지 않음 → 물리/가상 키보드 엔터 시 상위에서 동일하게 처리 가능
      }
    };

    const handleBeforeInput = (e: InputEvent) => {
      if (
        e.inputType === 'insertParagraph' ||
        e.inputType === 'insertLineBreak' ||
        (e.inputType === 'insertText' && (e.data?.includes('\n') || e.data?.includes('\r')))
      ) {
        e.preventDefault();
        // 가상 키보드만 insertLineBreak로 올 수 있어 keydown이 없을 수 있음 → 커스텀 이벤트로 상위에 알림
        if (e.inputType === 'insertParagraph' || e.inputType === 'insertLineBreak') {
          mathField.dispatchEvent(new CustomEvent('mathlive-enter-prevented', { bubbles: true }));
        }
      }
    };

    // 4. Shadow DOM 스타일 강제 (내부 버튼 숨기기 포함)
    const shadowRoot = mathField.shadowRoot;
    if (shadowRoot) {
      const style = document.createElement('style');
      style.textContent = `
        /* 내부 컨테이너 높이 및 정렬 */
        .ML__fieldcontainer {
          display: flex !important;
          align-items: center !important;
          height: 100% !important;
          width: 100% !important;
        }

        /* 내부 입력 필드 가로 스크롤 허용 */
        .ML__fieldcontainer__field {
          flex: 1 !important;
          overflow-x: auto !important;
          overflow-y: hidden !important;
          white-space: nowrap !important;
        }
      `;
      shadowRoot.appendChild(style);
    }

    mathField.addEventListener('keydown', handleKeyDown, true);
    mathField.addEventListener('beforeinput', handleBeforeInput as EventListener, true);

    return () => {
      mathField.removeEventListener('keydown', handleKeyDown, true);
      mathField.removeEventListener('beforeinput', handleBeforeInput as EventListener, true);
    };
  }, []);

  return (
    <div
      className={cn(
        'group flex items-center border border-border rounded-md w-full h-10 overflow-hidden bg-white px-2 focus-within:ring-1 focus-within:ring-ring',
        classNames?.container,
      )}
    >
      {/* 1. 실제 입력 영역 */}
      <math-field
        ref={mathFieldRef}
        className={cn(className, classNames?.mathField, 'focus:outline-none flex-1 h-full min-w-0')}
        virtual-keyboard-policy="manual"
        {...props}
      >
        {children ?? ''}
      </math-field>

      <Toggle
        onClick={toggleVirtualKeyboard}
        variant="default"
        size="sm"
        className="text-muted-foreground data-[state=on]:text-primary"
      >
        <KeyboardIcon className="size-5" />
      </Toggle>
    </div>
  );
});

MathLive.displayName = 'MathLive';
