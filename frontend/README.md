# Clova Tutor Frontend

클로바 튜터 서비스의 프론트엔드 프로젝트입니다.

## 빠른 시작

### 사전 요구사항

- **Node.js** 18 이상
- **Yarn** 4.12.0 이상
- **백엔드 서버**: 루트 디렉터리에서 Docker로 실행 중 (`localhost:8000`)

### 설치 및 실행

```bash
# 의존성 설치
yarn install

# 개발 서버 실행 (http://localhost:5173)
yarn dev
```

**개발 모드**에서는 루트에서 Docker로 호스팅된 백엔드 서버(`localhost:8000`)와 자동으로 연결됩니다.

### 빌드

```bash
# 프로덕션 빌드
yarn build

# 개발 환경 빌드
yarn build:dev

# 빌드 결과 미리보기
yarn preview
```

## 주요 스크립트

| 명령어 | 설명 |
|--------|------|
| `yarn dev` | 개발 서버 시작 (Vite) |
| `yarn build` | 프로덕션 빌드 |
| `yarn build:dev` | 개발 환경 빌드 |
| `yarn preview` | 빌드 결과 미리보기 |
| `yarn format` | 코드 포맷팅 (Biome) |

### 고급 스크립트

| 명령어 | 설명 | 상세 문서 |
|--------|------|-----------|
| `yarn api:generate` | Swagger 스펙으로 API 클라이언트 생성 | [API 생성 가이드](docs/API_GENERATION.md) |
| `yarn mock:convert` | HAR 파일을 MSW Mock으로 변환 | [Mock 설정 가이드](docs/MOCK_SETUP.md) |
| `yarn router:generate` | TanStack Router 라우트 자동 생성 | - |
| `yarn test:e2e` | E2E 테스트 실행 (Playwright) | [E2E 테스트 가이드](docs/E2E_TESTING.md) |
| `yarn test:codegen` | Playwright 테스트 코드 생성기 | [E2E 테스트 가이드](docs/E2E_TESTING.md) |
| `yarn test:generate-stubs` | QA 시트 기반 테스트 스텁 생성 | [E2E 테스트 가이드](docs/E2E_TESTING.md) |

## 환경 설정

개발 환경에서는 기본값으로 `localhost:8000`의 백엔드 서버를 사용합니다.

### 환경 변수

```env
# 백엔드 API 기본 URL (개발 환경)
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 프로젝트 구조

```
clova-tutor-fe/
├── src/
│   ├── app/           # 앱 설정 (Router, Provider 등)
│   ├── pages/         # 페이지 컴포넌트 (TanStack Router)
│   ├── widgets/       # 복합 위젯
│   ├── features/      # 기능 단위 모듈
│   ├── entities/      # 도메인 엔티티
│   ├── shared/        # 공유 리소스
│   └── packages/      # 내부 패키지
├── mocks/             # MSW Mock 데이터
├── playwright/        # E2E 테스트
└── scripts/           # 유틸리티 스크립트
```

## 라이선스

MIT License
