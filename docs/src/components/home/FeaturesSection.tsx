/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import Translate, { translate } from '@docusaurus/Translate';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function FeaturesSection() {
  const philosophyItems = [
    {
      illustration: "/img/connected-learning-flow.png",
      title: translate({ id: 'features.connectedLearning.title', message: '연결된 학습 흐름' }),
      description: translate({
        id: 'features.connectedLearning.description',
        message: '문제 풀이가 단절되지 않고, 대화를 통해 다음 학습으로 이어지는 구조',
      }),
    },
    {
      illustration: "/img/context-aware-conversation.png",
      title: translate({ id: 'features.contextAware.title', message: '대화 중심 학습 경험' }),
      description: translate({
        id: 'features.contextAware.description',
        message: '이전 질문과 풀이 맥락을 유지하며 학습 대화를 이어가는 튜터',
      }),
    },
    {
      illustration: "/img/supportive-not-replacing.png",
      title: translate({ id: 'features.supportive.title', message: '보조적 AI 설계 철학' }),
      description: translate({
        id: 'features.supportive.description',
        message: 'AI가 모든 판단을 대신하지 않고, 학습자가 사고를 이어갈 수 있도록 개입의 범위를 조절하는 튜터',
      }),
    },
  ];

  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold mb-6 text-center">
            Design Principles
          </h2>

          <div className="max-w-3xl mx-auto mb-12 space-y-4 text-center">
            <p className="text-base md:text-lg text-muted-foreground leading-relaxed break-keep">
              <Translate id="features.intro1">
                CLOVA Tutor는 학습자가 스스로 사고를 이어갈 수 있도록 돕는 대화형 학습 파트너가 되도록 설계되었습니다.
              </Translate>
            </p>
            <p className="text-base md:text-lg text-muted-foreground leading-relaxed break-keep">
              <Translate id="features.intro2">
                본 프로젝트에서 선택한 대화 기반 학습 UX와 AI 튜터 설계의 핵심 기준을 소개합니다.
              </Translate>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {philosophyItems.map((item, index) => (
              <div
                key={index}
                className="bg-card rounded-xl p-6 border border-border text-center"
              >
                <div className="flex items-center justify-center mb-5">
                  <img
                    src={useBaseUrl(item.illustration)}
                    alt={item.title}
                    className="w-60"
                  />
                </div>
                <h3 className="text-lg font-semibold mb-3 text-foreground">
                  {item.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed break-keep">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
