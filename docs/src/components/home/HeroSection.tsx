/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import Link from "@docusaurus/Link";
import Translate, { translate } from "@docusaurus/Translate";
import useBaseUrl from "@docusaurus/useBaseUrl";

export default function HeroSection() {
  return (
    <section className="relative py-20 overflow-hidden">
      {/* Background - Modern gradient mesh (top only) */}
      <div className="absolute inset-x-0 top-0 h-[500px] -z-10 overflow-hidden">
        {/* Gradient mesh overlay */}
        <div
          className="absolute inset-0 opacity-30 dark:opacity-20"
          style={{
            background: `
              radial-gradient(ellipse 80% 50% at 20% -20%, rgba(237, 51, 166, 0.15), transparent),
              radial-gradient(ellipse 60% 40% at 80% -10%, rgba(0, 206, 255, 0.15), transparent),
              radial-gradient(ellipse 40% 30% at 50% 10%, rgba(147, 63, 240, 0.1), transparent)
            `,
          }}
        />
        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(147, 63, 240, 0.5) 1px, transparent 1px),
              linear-gradient(90deg, rgba(147, 63, 240, 0.5) 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      <div className="container mx-auto px-4 space-y-20">
        <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
          {/* Subtitle */}
          <p className="mb-2 text-sm md:text-base text-muted-foreground font-medium tracking-wide break-keep">
            <Translate id="hero.subtitle">교육용 대화형 AI 튜터 오픈소스 데모 프로젝트</Translate>
          </p>

          {/* Logo */}
          <img
            src={useBaseUrl("/img/title-logo.svg")}
            alt="CLOVA Tutor"
            className="h-16 md:h-22 mb-6"
          />

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/docs/user-guide/start"
              className="px-8 py-4 rounded-lg bg-primary text-white font-semibold hover:bg-primary/90 transition-colors no-underline hover:no-underline"
            >
              <Translate id="hero.userGuide">사용자 가이드</Translate>
            </Link>
            <Link
              to="/docs/dev-guide/quick-start"
              className="px-8 py-4 rounded-lg border border-border text-muted-foreground font-semibold hover:bg-accent hover:text-accent-foreground transition-colors no-underline hover:no-underline"
            >
              <Translate id="hero.installGuide">설치 가이드</Translate>
            </Link>
          </div>
        </div>

        <div className="w-full flex justify-center items-center">
          {/* Hero Image */}
          <img
            src={useBaseUrl("/img/hero-img.png")}
            alt={translate({ id: 'hero.imageAlt', message: 'CLOVA Tutor 서비스 화면' })}
            className="md:max-w-5xl object-contain"
            width={1500}
          />
        </div>
      </div>
    </section>
  );
}
