/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */


export default function ComparisonSection() {
  return (
    <section className="py-20 bg-gray-50 dark:bg-gray-900/50">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900 dark:text-white">
            다른 AI 튜터와 뭐가 다른가요? 🤷‍♀️
          </h2>
          <div className="max-w-3xl mx-auto bg-blue-100 dark:bg-blue-900/30 rounded-2xl p-6">
            <p className="text-lg text-gray-700 dark:text-gray-300">
              🗣️ "AI 튜터가 다 비슷하지 않나요?"
              <br />
              🙅‍♂️ 전혀 그렇지 않아요! 우리만의 특별한 점이 있답니다.
            </p>
          </div>
        </div>

        {/* Comparison Cards */}
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
            {/* Traditional AI Tutor */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">🤖</span>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    기존 AI 튜터
                  </h3>
                </div>
                <p className="text-lg font-semibold text-gray-600 dark:text-gray-400 mb-4">
                  → 정해진 답변 중심
                </p>
              </div>
              <hr className="border-gray-200 dark:border-gray-700 mb-6" />
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <span className="text-gray-400 mt-1">•</span>
                  <span className="text-gray-600 dark:text-gray-300">
                    "이 문제의 답은 이거야."
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-gray-400 mt-1">•</span>
                  <span className="text-gray-600 dark:text-gray-300">
                    결과만 알려주는 방식
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-gray-400 mt-1">•</span>
                  <span className="text-gray-600 dark:text-gray-300">수동적 학습</span>
                </li>
              </ul>
            </div>

            {/* VS Divider */}
            <div className="flex items-center justify-center">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full w-20 h-20 flex items-center justify-center text-2xl font-bold shadow-xl">
                VS
              </div>
            </div>

            {/* Our AI Tutor */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-2xl p-8 shadow-xl border-2 border-blue-200 dark:border-blue-800">
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">🚀</span>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    CLOVA Tutor
                  </h3>
                </div>
                <p className="text-lg font-semibold text-blue-600 dark:text-blue-400 mb-4">
                  → 질문과 대화 중심
                </p>
              </div>
              <hr className="border-blue-200 dark:border-blue-800 mb-6" />
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <span className="text-blue-500 mt-1">•</span>
                  <span className="text-gray-700 dark:text-gray-200 font-medium">
                    "이 부분은 어떻게 생각해?"
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-500 mt-1">•</span>
                  <span className="text-gray-700 dark:text-gray-200 font-medium">
                    과정을 함께 탐구하는 방식
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-500 mt-1">•</span>
                  <span className="text-gray-700 dark:text-gray-200 font-medium">
                    능동적 사고력 증진
                  </span>
                </li>
              </ul>
            </div>
          </div>

          {/* Key Difference Highlight */}
          <div className="mt-12 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-950/40 dark:to-purple-950/40 rounded-2xl p-8 border-l-4 border-blue-500">
            <div className="flex items-start gap-4">
              <span className="text-4xl flex-shrink-0">👉🏻</span>
              <div>
                <p className="text-lg md:text-xl text-gray-800 dark:text-gray-200 leading-relaxed">
                  <strong>핵심 차이점:</strong> 우리는 학생에게 질문을 던지고, 단계별로 끊어서 설명해줘요.
                  마치 옆에서 함께 고민해주는 친구처럼요!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
