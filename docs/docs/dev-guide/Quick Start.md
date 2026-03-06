---
slug: quick-start
sidebar_position: 1
---

### Prerequisites

실행하기에 앞서 다음의 툴들이 설치되어 있어야 합니다.

- [Docker](https://docs.docker.com/get-docker/) / [Docker Compose](https://docs.docker.com/compose/install/) : 컨테이너화 플랫폼
- [uv](https://docs.astral.sh/uv/getting-started/installation/) : Python 의존성 관리 툴

### 0. 필수 환경 세팅

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 필수 환경 변수를 설정합니다.

```bash
cp .env.example .env
```

필수로 설정해야 하는 환경 변수:
- `HCX_API_KEY`
- `CLOVA_STUDIO_*` 관련 변수들

> 환경 변수에 대한 상세한 설명은 [환경 변수 구성](./environment-variables) 문서를 참고하세요.

### 1. 로컬 환경 시작

```
docker compose up -d
```

### 2. 백엔드 초기 세팅

샘플 데이터를 바탕으로 초기 데이터 세팅
```
cd backend && make init
```

### 3. 모델 서버 초기 세팅
샘플 데이터를 바탕으로 모델 서버 초기 데이터 세팅

```
cd model-server && make setup
```

### 4. 서비스 확인

- Web UI: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs) 

