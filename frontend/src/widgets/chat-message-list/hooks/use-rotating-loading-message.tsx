/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useEffect, useMemo, useState } from 'react';
import { useSubject } from '@/entities/chats/hooks/use-subject';

const MATH_LOADING_MESSAGES = [
  [
    '답변을 생각하고 있어요... 🚀',
    '조금만 더 생각해볼게요!',
    '수학의 숲을 헤매는 중이에요 🌲',
    '수학적 직관을 총동원 중…✨',
    '논리적으로 사고하는 중이에요',
    '머릿속에서 수를 굴리는 중이에요...',
    '수식의 흐름을 따라가는 중이에요',
    '수학적인 직관을 끌어오는 중이에요',
    '풀이의 실마리를 찾는 중이에요...',
    '사고 회로를 정리하는 중이에요',
    '계산기 없이 계산 중... (진짜예요!)',
  ],
  [
    '답변을 생각하고 있어요... 🚀',
    '생각을 정리하는 중이에요...',
    '차근차근 단계를 되짚는 중이에요',
    '문제의 구조를 다시 살펴보는 중이에요',
    '숫자들이 어떻게 흘러가는지 보고 있어요',
    '여러 풀이 중 가장 명확한 걸 고르는 중이에요',
    '변수가 어떤 역할을 하는지 정리하고 있어요',
    '논리적 흐름이 끊기지 않게 조율하는 중이에요',
    '무리수처럼 끝이 안 보이네요… 조금만 기다려주세요!',
    '논리의 미궁을 빠져나오는 중이에요… 🌀',
    '수학적 우아함을 추구하는 중이에요 ✨',
    '혹시 실수한 부분이 없는지 살펴보는 중이에요',
  ],
  [
    '답변을 생각하고 있어요... 🚀',
    '다양한 접근법을 비교하고 있어요.',
    '수학적 타당성을 확인하고 있어요.',
    '수학 신전에서 영감을 받아오는 중이에요 🏛️',
    '계산기랑 철학적인 대화를 나누는 중이에요',
    '관련 개념이나 성질을 다시 떠올리고 있어요',
    '헷갈리는 개념은 없는지 점검 중이에요',
    '풀이가 더 잘 보이게 정리하고 있어요',
    '생각이 끊기지 않도록 집중하고 있어요',
    '기본 개념부터 다시 차근차근 정리 중이에요',
    '추측 대신 확실한 논리만 남기고 있어요',
    '정답까지 전 과정을 체크하고 있어요',
    '시간 안에 정확히 풀기 위해 집중하는 중이에요',
    '더 잘 이해할 수 있도록 문장을 정리하고 있어요',
  ],
];

const ENGLISH_LOADING_MESSAGES = [
  [
    '답변을 생각하고 있어요... 🚀',
    '조금만 더 생각해볼게요!',
    '알파벳을 찾아보는 중이에요',
    '단어를 되새기는 중이에요...',
    '영어사전을 뒤적이는 중이에요',
    '표현을 정리하는 중이에요',
    '머릿속에서 문장을 조합하는 중이에요',
    '언어감각을 끌어올리는 중이에요!',
    '차분히 다시 읽어보는 중이에요',
    '문장의 흐름을 떠올리는 중이에요',
    '말맛을 다듬는 중이에요',
    '자연스러운 표현을 찾는 중이에요!',
  ],
  [
    '답변을 생각하고 있어요... 🚀',
    '머릿속 영어 사전을 뒤적이는 중이에요...',
    '언어 감각에 집중하는 중이에요',
    '표현이 매끄러운지 입으로 조용히 말해보는 중이에요',
    '자연스러운 리듬을 살피는 중이에요 🎶',
    '학생 눈높이에 맞는 문장을 만들고 있어요',
    '어떤 예시가 가장 직관적일지 고민 중이에요',
    '쉽고 명확한 문장을 고르는 중이에요',
    '어색하지 않게 다듬는 중이에요 ✍️',
    '긴 문장을 짧게 바꿔보는 중이에요',
  ],
  [
    '답변을 생각하고 있어요... 🚀',
    '문장을 머릿속에서 조용히 읽고 있어요',
    '의미가 더 잘 전달되도록 다듬는 중이에요',
    '비슷한 단어들 사이에서 고민 중이에요...',
    '뉘앙스를 비교하고 있어요 🔍',
    '문법 감각을 곱씹는 중이에요',
    '말하고 싶은 의도를 다시 정리하는 중이에요',
    '전달력이 좋은 문장을 만들고 있어요!',
    '자연스럽게 들리는지 스스로 말해보는 중이에요',
    '무슨 어조가 더 적절할지 생각 중이에요',
    '학생 입장에서 이해하기 쉬운 표현을 찾는 중이에요 ✨',
  ],
];

export function useRotatingLoadingMessage() {
  const { isMathSubject } = useSubject();
  const [messageIndex, setMessageIndex] = useState(0);

  const loadingGroups = useMemo(() => {
    return isMathSubject ? MATH_LOADING_MESSAGES : ENGLISH_LOADING_MESSAGES;
  }, [isMathSubject]);

  const selectedGroup = useMemo(() => {
    const randomIndex = Math.floor(Math.random() * loadingGroups.length);
    return loadingGroups[randomIndex];
  }, [loadingGroups]);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % selectedGroup.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [selectedGroup]);

  return selectedGroup[messageIndex];
}
