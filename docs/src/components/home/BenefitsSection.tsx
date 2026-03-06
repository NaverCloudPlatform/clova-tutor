/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */


interface BenefitCardProps {
  icon: string;
  title: string;
  description: string[];
}

function BenefitCard({ icon, title, description }: BenefitCardProps) {
  return (
    <div className="flex gap-6 p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border-l-4 border-blue-500">
      <div className="flex-shrink-0">
        <div className="text-5xl">{icon}</div>
      </div>
      <div className="flex-1">
        <h3 className="text-xl font-bold mb-3 text-blue-600 dark:text-blue-400">
          {title}
        </h3>
        <div className="space-y-2">
          {description.map((text, index) => (
            <p key={index} className="text-gray-600 dark:text-gray-300 leading-relaxed">
              {text}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function BenefitsSection() {
  const benefits = [
    {
      icon: '🔁',
      title: '문제 풀이 시도 증가',
      description: [
        '어려운 문제를 만나도 "끝까지 도전해보자!"는 마음으로 더 많이 시도하게 될 거예요.',
        'AI 튜터의 가이드를 따르면서, 포기하는 대신 도전하는 습관을 만들 수 있어요.',
      ],
    },
    {
      icon: '🔍',
      title: '능동적 학습 능력 증진',
      description: [
        'AI 튜터는 학생의 궁금증을 자극해서 질문하는 습관을 길러줘요.',
        '스스로 궁금해하고 탐구하는 능력이 생기면 학습의 폭이 훨씬 넓어질 거예요!',
      ],
    },
  ];

  return (
    <section className="py-20 bg-white dark:bg-gray-900">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900 dark:text-white">
            기대할 수 있는 효과 ✨
          </h2>
          <div className="max-w-2xl mx-auto bg-blue-100 dark:bg-blue-900/30 rounded-2xl p-6">
            <p className="text-lg text-gray-700 dark:text-gray-300">
              CLOVA Tutor와 함께 공부하면 이런 변화를 경험할 수 있어요.
            </p>
          </div>
        </div>

        {/* Benefits List */}
        <div className="max-w-4xl mx-auto space-y-6">
          {benefits.map((benefit, index) => (
            <BenefitCard key={index} {...benefit} />
          ))}
        </div>
      </div>
    </section>
  );
}
