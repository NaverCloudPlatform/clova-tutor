/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { VirtualKeyboardLayout } from 'mathlive';

export const CALCULUS_ROWS: VirtualKeyboardLayout = {
  label: '미적분',
  rows: [
    ['(', ')', '|', '[', ']', '\\sqrt{#0}', '\\sqrt[3]{#0}', '\\geq', '\\leq', '<', '>'],
    [
      '\\sum',
      '\\int',
      'f(x)',

      '\\frac{#@}{#?}',
      '#@^{#?}',
      '#@_{#?}',
      '\\log_{#?}{#@}',
      '\\lim_{n\\to{#?}}',
      '\\ln',
      '[backspace]',
    ],
    ['\\sin', '\\cos', '\\tan', '\\theta', '\\pi', '=', '[left]', '[right]', '[return]'],
  ],
};
