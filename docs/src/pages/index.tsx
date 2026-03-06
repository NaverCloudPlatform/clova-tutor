/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { ReactNode } from 'react';
import Layout from '@theme/Layout';
import { translate } from '@docusaurus/Translate';
import FeaturesSection from '@/components/home/FeaturesSection';
import HeroSection from '@/components/home/HeroSection';
import OverviewSection from '@/components/home/OverviewSection';
import { WhoIsForSection } from "@/components/home/WhoIsForSection";


export default function Home(): ReactNode {
  return (
    <Layout
      title="CLOVA Tutor"
      description={translate({
        id: 'homepage.description',
        message: '교육용 대화형 AI 튜터 설계를 위한 오픈소스 데모 프로젝트. 수학·영어 문제 풀이, 개념 설명, 학습 목표 설정, 복습 관리를 통합적으로 경험하세요.',
      })}
    >
      <HeroSection />
      <OverviewSection />
      <WhoIsForSection />
      <FeaturesSection />
    </Layout>
  );
}
