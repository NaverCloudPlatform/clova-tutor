/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute, Link } from '@tanstack/react-router';
import { BookOpenTextIcon, CircleArrowRightIcon, HandIcon } from 'lucide-react';
import { Button } from '@/shared/ui/button';

export const Route = createFileRoute('/_student/$subject/')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="flex flex-col h-full">
      <div className="h-12" />

      <div className="flex flex-col justify-center sm:gap-y-28 gap-y-8 w-fit mx-auto @2xl/sidebar-inset:min-w-3xl @lg:max-w-3xl flex-1 px-4 sm:py-20 py-6">
        <div className="flex flex-col gap-y-6">
          <div className="flex flex-col gap-y-5">
            <img src="/title-logo.svg" alt="클로바 튜터 로고 이미지" width={258} height={80} className="h-13" />
            <h1 className="text-2xl font-semibold">클로바 튜터</h1>
          </div>
          <div className="text-foreground-weak flex flex-col gap-y-2">
            <p>
              안녕! 만나서 반가워~ 나는 공부 친구, 클로바 튜터야
              <HandIcon className="size-4 inline ms-1 mb-0.5 rotate-20" />
            </p>
            <p>앞으로 나와 함께 즐겁게 공부하며 차근차근 성장해보자!</p>
            <p>
              어떤 과목부터 시작하고 싶니?
              <BookOpenTextIcon className="size-4 ms-1 inline" />
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 @2xl/sidebar-inset:grid-cols-2 gap-4">
          <Link from="/" to="/$subject/chats" params={{ subject: 'math' }} className="flex-1">
            <SubjectButton
              subject="수학"
              description={['어떤 수학 문제든', '정확하게 풀이 과정을 설명해주는', '나만의 수학 공부 친구']}
            />
          </Link>

          <Link from="/" to="/$subject/chats" params={{ subject: 'english' }} className="flex-1">
            <SubjectButton
              subject="영어"
              description={['어떤 영어 문제든', '정확하게 풀이 과정을 설명해주는', '나만의 영어 공부 친구']}
            />
          </Link>
        </div>
      </div>

      {/* MEMO: 온보딩 페이지로 전환 시 높이를 맞추기 위해 추가 */}
      <div className="h-39 w-full sm:block hidden" />
    </div>
  );
}

type Props = {
  subject: string;
  description: string[];
};

function SubjectButton({ subject, description }: Props) {
  return (
    <Button
      variant="outline"
      size="free"
      className="flex flex-col items-start justify-between gap-y-3 px-5 py-4 min-h-42 w-full hover:bg-secondary"
    >
      <div className="flex items-center justify-between w-full">
        <h2 className="text-lg font-medium">{subject}</h2>
        <CircleArrowRightIcon className="stroke-border size-6" />
      </div>

      <div className="flex items-end justify-between gap-x-4 lg:gap-x-16 w-full font-normal">
        <div className="flex flex-col gap-y-1.5">
          {description.map((item) => (
            <p key={item} className="text-left whitespace-pre-wrap text-foreground-weak">
              {item}
            </p>
          ))}
        </div>
      </div>
    </Button>
  );
}
