/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import Translate from "@docusaurus/Translate";

export default function OverviewSection() {
  return (
    <section className="py-20 bg-muted">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto text-center">
          {/* Section Header */}
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            Project Overview
          </h2>

          {/* Identity */}
          <p className="text-lg md:text-xl text-muted-foreground leading-relaxed mb-6 break-keep">
            <Translate id="overview.identity">
              CLOVA Tutor는 NAVER Cloud의 HCX-005 모델을 기반으로, 한국 K-12 학습 환경에서 교육용 대화형 AI 튜터를 어떻게 설계할 것인지를 탐구하는 데모 프로젝트입니다.
            </Translate>
          </p>

          {/* Context */}
          <p className="text-base md:text-lg text-muted-foreground leading-relaxed mb-10 break-keep">
            <Translate id="overview.context">
              이 프로젝트는 하나의 채팅 인터페이스 안에서 문제 풀이, 개념 설명, 추가 질문, 복습으로 이어지는 학습 대화의 구조를 어떻게 설계할 수 있는지를 중심으로 구성되어 있습니다.
            </Translate>
          </p>

          {/* Declaration */}
          <div className="bg-secondary rounded-xl px-6 py-5">
            <p className="text-sm md:text-base text-muted-foreground mb-0 break-keep">
              <Translate id="overview.declaration">
                이 프로젝트는 학습 성과 자체보다, 대화 중심 학습 경험을 어떻게 구조화할 수 있는지에 대한 설계 관점을 공유합니다.
              </Translate>
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
