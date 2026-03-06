/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import Translate, { translate } from '@docusaurus/Translate';

export function WhoIsForSection() {
  const audiences = [
    {
      title: translate({ id: 'whoIsFor.developer.title', message: '교육용 AI 튜터를 설계하는 개발자' }),
      description: translate({ id: 'whoIsFor.developer.description', message: '모델 구조와 대화 흐름을 레퍼런스로 보고 싶은 분' }),
    },
    {
      title: translate({ id: 'whoIsFor.pm.title', message: '학습 서비스 기획자 / PM' }),
      description: translate({ id: 'whoIsFor.pm.description', message: 'LLM 기반 학습 대화 구조를 고민하는 분' }),
    },
    {
      title: translate({ id: 'whoIsFor.team.title', message: 'LLM 시스템 설계 팀' }),
      description: translate({ id: 'whoIsFor.team.description', message: 'ReAct · Tool-based 구조를 실제 서비스 맥락에서 참고하고 싶은 팀' }),
    },
    {
      title: translate({ id: 'whoIsFor.researcher.title', message: '포트폴리오 · 연구 목적 사용자' }),
      description: translate({ id: 'whoIsFor.researcher.description', message: '교육용 AI 시스템 설계 사례를 찾는 분' }),
    },
  ];

  return (
    <section className="py-24 bg-muted/60">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center mb-14">
          <h2 className="text-2xl md:text-3xl font-bold mb-3 text-foreground">
            Who is CLOVA Tutor For?
          </h2>
          <p className="text-muted-foreground text-base md:text-lg leading-relaxed">
            <Translate id="whoIsFor.subtitle">
              CLOVA Tutor는 다음과 같은 사람들을 위한 설계 레퍼런스입니다.
            </Translate>
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-5xl mx-auto">
          {audiences.map((item, index) => (
            <AudienceCard
              key={index}
              index={index + 1}
              title={item.title}
              description={item.description}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

function AudienceCard({
  index,
  title,
  description,
}: {
  index: number;
  title: string;
  description: string;
}) {
  return (
    <div
      className="group relative rounded-xl border border-border bg-card p-6 pl-7
        transition-all duration-200 ease-out
        hover:border-primary/40 hover:shadow-md hover:shadow-primary/5
        focus-within:ring-2 focus-within:ring-primary/20"
    >
      {/* Left accent bar */}
      <div
        className="absolute left-0 top-5 bottom-5 w-1 rounded-full bg-primary/80
          opacity-80 group-hover:opacity-100 transition-opacity"
        aria-hidden
      />

      {/* Number badge */}
      <div
        className="inline-flex size-8 items-center justify-center rounded-lg
          bg-primary/12 text-primary text-sm font-semibold mb-4
          group-hover:bg-primary/20 transition-colors"
      >
        {index}
      </div>

      <h3 className="text-base font-semibold text-foreground mb-2 leading-snug">
        {title}
      </h3>
      <p className="text-sm text-muted-foreground leading-relaxed">
        {description}
      </p>
    </div>
  );
}
