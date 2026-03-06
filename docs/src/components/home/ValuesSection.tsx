/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */


interface ValueCardProps {
  icon: string;
  title: string;
  description: string[];
}

function ValueCard({ icon, title, description }: ValueCardProps) {
  return (
    <div className="group relative bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100 dark:border-gray-700">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <div className="relative">
        <div className="text-5xl mb-4">{icon}</div>
        <h3 className="text-2xl font-bold mb-4 text-blue-600 dark:text-blue-400">
          {title}
        </h3>
        <div className="space-y-3">
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

export default function ValuesSection() {
  const values = [
    {
      icon: '🎯',
      title: '자기주도학습 능력',
      description: [
        '학생 스스로 틀린 이유를 파악하고 해결 방법을 찾아가는 능력을 길러줄 수 있어요.',
        '학습 과정에서 도움이 될 만한 추가 학습 자료를 통해 이해도가 높아질 거예요!',
      ],
    },
    {
      icon: '💪🏻',
      title: '포기하지 않는 마음',
      description: [
        '어려운 문제를 만나도 "할 수 있다!"는 마음이 들도록 응원해줘요.',
        '실패도 배움의 과정이라는 걸 이해하며 성장할 수 있을 거예요.',
      ],
    },
    {
      icon: '🤔',
      title: '단계별 사고 과정',
      description: [
        '복잡한 문제를 작은 단위로 나누어 차근차근 접근해요.',
        '각 단계에서 "왜 이렇게 해야 하는지"를 이해하며 진행할 수 있어요.',
      ],
    },
    {
      icon: '📈',
      title: '성취감과 자신감',
      description: [
        '스스로 해결한 문제들이 점점 쌓이면서 자연스럽게 자신감이 생겨요.',
        '더 어려운 문제에도 도전하고 싶어질 거예요!',
      ],
    },
  ];

  return (
    <section className="py-20 bg-gray-50 dark:bg-gray-900/50">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900 dark:text-white">
            CLOVA Tutor가 추구하는 가치 💡
          </h2>
          <div className="max-w-3xl mx-auto bg-blue-100 dark:bg-blue-900/30 rounded-2xl p-6">
            <p className="text-lg md:text-xl text-gray-700 dark:text-gray-300 leading-relaxed">
              <strong>장기적인 학업 성취도 향상</strong>이 목표예요. 단기간에 점수를 올리는 것보다,
              <br />
              평생 도움이 될 문제 해결 능력과 사고력을 기르는 것이 더 중요하다고 생각해요!
            </p>
          </div>
        </div>

        {/* Values Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {values.map((value, index) => (
            <ValueCard key={index} {...value} />
          ))}
        </div>
      </div>
    </section>
  );
}
