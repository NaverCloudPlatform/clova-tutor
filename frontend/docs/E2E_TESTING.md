# E2E 테스트 자동화

Playwright를 사용한 E2E 테스트와 QA 시트 기반 자동화 가이드입니다.

## 목차

- [개요](#개요)
- [빠른 시작](#빠른-시작)
- [테스트 실행](#테스트-실행)
- [테스트 작성](#테스트-작성)
- [Playwright Codegen](#playwright-codegen)
- [자동 스텁 생성](#자동-스텁-생성)
- [참고 자료](#참고-자료)

## 개요

이 프로젝트는 다음 도구들로 E2E 테스트를 자동화합니다:

- **Playwright**: 브라우저 자동화 및 테스트 실행
- **MSW**: API Mocking으로 안정적인 테스트
- **e2e-autogen**: QA 시트에서 테스트 스텁 자동 생성

## 빠른 시작

### 설치

```bash
# Playwright 브라우저 설치
npx playwright install
```

### 첫 번째 테스트 실행

```bash
# 모든 테스트 실행
yarn test:e2e

# 특정 테스트만 실행
yarn test:e2e tc4.chat-input.spec.ts

# UI 모드로 실행 (디버깅)
npx playwright test --ui
```

## 테스트 실행

### 기본 명령어

```bash
# 모든 테스트 실행 (Headless)
yarn test:e2e

# 브라우저 표시하며 실행
yarn test:e2e --headed

# 특정 브라우저만
yarn test:e2e --project=chromium
```

### UI 모드 (권장)

```bash
npx playwright test --ui
```

UI 모드 기능:
- 실시간 테스트 실행 과정 시각화
- 특정 스텝 재실행 및 디버깅
- 테스트 결과 상세 분석

### 리포트 확인

```bash
# HTML 리포트 생성 및 열기
npx playwright show-report
```

## 테스트 작성

### 테스트 파일 구조

```
playwright/
├── e2e/
│   ├── tc1.login.spec.ts           # 로그인 테스트
│   ├── tc2.home.spec.ts            # 홈 화면 테스트
│   ├── tc3.chat-management.spec.ts # 채팅 관리
│   ├── tc4.chat-input.spec.ts      # 채팅 입력
│   ├── tc5.goal.spec.ts            # 목표 시스템
│   ├── tc6.chat-render.spec.ts     # 채팅 렌더링
│   ├── tc7.problem-content.spec.ts # 학습 콘텐츠
│   └── tc8.problem-note.spec.ts    # 학습 노트
├── __generated-stub__/
│   └── TC-4.stub.ts                # 자동 생성된 스텁
└── setup/
    └── auth.setup.ts               # 인증 설정
```

### MSW와 함께 사용

```typescript
test('TC-4.2: 스트리밍 응답 테스트', async ({ page }) => {
  // Mock 시나리오 활성화
  await page.goto('http://localhost:5173?scenario=TC-4.2');

  await page.goto('http://localhost:5173/math/chats/314');

  // 메시지 전송
  await page.fill('textarea', '피타고라스 정리 설명해줘');
  await page.click('button[type="submit"]');

  // 스트리밍 응답 확인 (Mock 데이터로 즉시 응답)
  await expect(page.locator('.assistant-message')).toBeVisible();
  await expect(page.locator('.assistant-message')).toContainText('피타고라스');
});
```

Mock 시나리오 설정은 [Mock 설정 가이드](MOCK_SETUP.md)를 참고하세요.

## Playwright Codegen

브라우저 조작을 녹화하여 테스트 코드를 자동 생성합니다.

자세한 내용: https://playwright.dev/docs/codegen

### 사용법

```bash
# Codegen 시작
yarn test:codegen

# 특정 URL에서 시작
yarn test:codegen http://localhost:5173/math/chats/314
```

브라우저에서 원하는 동작을 수행하면 Inspector 창에 테스트 코드가 자동으로 생성됩니다.

## 자동 스텁 생성

### 개요

`@jjades/e2e-autogen` 라이브러리를 사용하여 [기능 QA 시트](https://docs.google.com/spreadsheets/d/1XLSwVLph3tIQcDUzazokn4ABbX0T-sUteDMe2-Z_oFk/edit?usp=sharing)에서 테스트 스텁 코드를 자동으로 생성합니다.

자세한 내용: [@jjades/e2e-autogen 문서](https://www.npmjs.com/package/@jjades/)

### 제한사항

현재 Google Sheets API 연동에 필요한 OAuth2 인증 파일이 오픈소스 프로젝트에 포함되지 않았습니다. 따라서 다음 기능은 동작하지 않습니다:

- ❌ QA 시트에서 자동으로 스텁 코드 동기화
- ❌ 테스트 실행 결과 QA 시트에 자동 업데이트

이 코드는 **동작 설명 및 참고용**으로 포함되어 있으며, 실제 프로젝트에서는 생성된 스텁 코드를 기반으로 테스트를 작성했습니다.

## 참고 자료

- [Playwright 공식 문서](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [@jjades/e2e-autogen NPM](https://www.npmjs.com/package/@jjades/)
- [기능 QA 시트](https://docs.google.com/spreadsheets/d/1XLSwVLph3tIQcDUzazokn4ABbX0T-sUteDMe2-Z_oFk/edit?usp=sharing)
