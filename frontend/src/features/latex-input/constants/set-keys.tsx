/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { ChevronLeft, ChevronRight, Delete, Space } from 'lucide-react';
import type { Key } from '../types/keys';

export const setKeys: Key[] = [
  // 1줄 - 괄호 & 집합 기호
  { label: '(', value: '(', action: 'text', tooltip: '왼쪽 괄호' },
  { label: ')', value: ')', action: 'text', tooltip: '오른쪽 괄호' },
  { label: '[', value: '[', action: 'text', tooltip: '왼쪽 대괄호' },
  { label: ']', value: ']', action: 'text', tooltip: '오른쪽 대괄호' },
  { label: '\\lbrace', value: '\\{', action: 'text', tooltip: '왼쪽 중괄호' },
  { label: '\\rbrace', value: '\\}', action: 'text', tooltip: '오른쪽 중괄호' },
  { label: '\\cup', value: '\\cup', action: 'latex', tooltip: '합집합' },
  { label: '\\cap', value: '\\cap', action: 'latex', tooltip: '교집합' },
  { label: 'A-B', value: '\\setminus', action: 'latex', tooltip: '차집합' },
  {
    label: '\\subseteq',
    value: '\\subseteq',
    action: 'latex',
    tooltip: '부분집합',
  },
  {
    label: '\\supseteq',
    value: '\\supseteq',
    action: 'latex',
    tooltip: '포함집합',
  },
  {
    label: '\\emptyset',
    value: '\\emptyset',
    action: 'latex',
    tooltip: '공집합',
  },

  // 2줄 - x + 숫자 7~9 + 순열/조합
  { label: 'x', value: 'x', action: 'text', tooltip: '문자 x' },
  { label: '7', value: '7', action: 'text', tooltip: '숫자 7' },
  { label: '8', value: '8', action: 'text', tooltip: '숫자 8' },
  { label: '9', value: '9', action: 'text', tooltip: '숫자 9' },
  { label: '_{}P_{}', value: '_{}P_{}', action: 'latex', tooltip: '순열' },
  { label: '_{}C_{}', value: '_{}C_{}', action: 'latex', tooltip: '조합' },
  {
    label: '_{} \\Pi _{}',
    value: '_{} \\Pi _{}',
    action: 'latex',
    tooltip: '중복순열',
  },
  { label: '_{}H_{}', value: '_{}H_{}', action: 'latex', tooltip: '중복조합' },
  { label: '\\in', value: '\\in', action: 'latex', tooltip: '원소' },
  { label: '\\notin', value: '\\notin', action: 'latex', tooltip: '원소 아님' },
  { label: '|A|', value: '|A|', action: 'latex', tooltip: '집합 원소 개수' },
  { label: '\\neg', value: '\\neg', action: 'latex', tooltip: '부정' },

  // 3줄 - y + 숫자 4~6 + 확률/기대값/분산
  { label: 'y', value: 'y', action: 'text', tooltip: '문자 y' },
  { label: '4', value: '4', action: 'text', tooltip: '숫자 4' },
  { label: '5', value: '5', action: 'text', tooltip: '숫자 5' },
  { label: '6', value: '6', action: 'text', tooltip: '숫자 6' },
  { label: 'P(A)', value: 'P(A)', action: 'latex', tooltip: '확률' },
  { label: 'P(A|B)', value: 'P(A|B)', action: 'latex', tooltip: '조건부확률' },
  { label: 'E(X)', value: 'E(X)', action: 'latex', tooltip: '기대값' },
  { label: 'V(X)', value: 'V(X)', action: 'latex', tooltip: '분산' },
  {
    label: '\\bar{X}',
    value: '\\bar{X}',
    action: 'latex',
    tooltip: '표본평균',
  },
  {
    label: '\\sigma^2',
    value: '\\sigma^2',
    action: 'latex',
    tooltip: '모분산',
  },
  { label: 'S', value: 'S', action: 'latex', tooltip: '표본표준편차' },
  { label: 'S^2', value: 'S^2', action: 'latex', tooltip: '표본분산' },

  // 4줄 - n + 숫자 1~3 + 평균/표준편차
  { label: 'n', value: 'n', action: 'text', tooltip: '문자 n' },
  { label: '1', value: '1', action: 'text', tooltip: '숫자 1' },
  { label: '2', value: '2', action: 'text', tooltip: '숫자 2' },
  { label: '3', value: '3', action: 'text', tooltip: '숫자 3' },
  { label: '\\mu', value: '\\mu', action: 'latex', tooltip: '모평균' },
  {
    label: '\\sigma',
    value: '\\sigma',
    action: 'latex',
    tooltip: '모표준편차',
  },
  { label: 'm', value: 'm', action: 'text', tooltip: '모평균 (m)' },
  {
    label: '\\bar{x}',
    value: '\\bar{x}',
    action: 'latex',
    tooltip: '산술평균',
  },
  { label: 'x_i', value: 'x_i', action: 'latex', tooltip: 'i번째 변량' },
  { label: '=', value: '=', action: 'text', tooltip: '같다' },
  { label: '<', value: '<', action: 'text', tooltip: '작다' },

  // 5줄 - 기호류
  { label: '>', value: '>', action: 'text', tooltip: '크다' },
  { label: ':', value: ':', action: 'text', tooltip: '비율, 구분' },
  { label: '%', value: '%', action: 'text', tooltip: '퍼센트 (%)' },
  { label: '0', value: '0', action: 'text', tooltip: '숫자 0' },

  {
    label: '\\forall',
    value: '\\forall',
    action: 'latex',
    tooltip: '모든 (for all)',
  },
  {
    label: '\\exists',
    value: '\\exists',
    action: 'latex',
    tooltip: '존재한다 (there exists)',
  },

  // 마지막 줄 - 조작키
  {
    label: <Space />,
    value: 'Space',
    className: 'col-span-3 w-full h-13 !text-4xl',
    action: 'keystroke',
    tooltip: '띄어쓰기',
  },
  {
    label: <ChevronLeft />,
    value: 'Left',
    action: 'keystroke',
    tooltip: '왼쪽 이동',
  },
  {
    label: <ChevronRight />,
    value: 'Right',
    action: 'keystroke',
    tooltip: '오른쪽 이동',
  },
  {
    label: <Delete />,
    value: 'Backspace',
    action: 'keystroke',
    tooltip: '지우기',
  },
  { label: '↵', value: 'Enter', action: 'keystroke', tooltip: '줄 바꿈' },
];
