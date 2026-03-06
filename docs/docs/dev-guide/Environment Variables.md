---
slug: environment-variables
sidebar_position: 2
---

# 환경 변수 구성

`.env.example` 파일을 복사하여 `.env` 파일을 생성한 후, 아래 가이드를 참고하여 환경 변수를 설정합니다.

```bash
cp .env.example .env
```

## 필수 환경 변수

로컬 환경에서 서비스를 실행하기 위해 **반드시** 설정해야 하는 환경 변수들입니다.

### CLOVA Studio

> API 키 발급 방법은 [CLOVA Studio 공식 문서](https://api.ncloud-docs.com/docs/ai-naver-clovastudio-summary)를 참고하세요.

| 변수명 | 설명 |
|--------|------|
| `HCX_API_KEY` | HyperCLOVA X API 키 |
| `CLOVA_STUDIO_URL` | CLOVA Studio API URL |
| `CLOVA_STUDIO_HOST` | CLOVA Studio 호스트 |
| `CLOVA_STUDIO_API_KEY` | CLOVA Studio API 키 |
| `CLOVA_STUDIO_GW_API_KEY` | CLOVA Studio Gateway API 키 |
| `CLOVA_STUDIO_REQUEST_ID` | CLOVA Studio 요청 ID |
| `CLOVA_STUDIO_APP_ID` | CLOVA Studio 앱 ID |

### Swagger UI

| 변수명 | 설명 |
|--------|------|
| `SWAGGER_USERNAME` | Swagger UI 사용자명 |
| `SWAGGER_PASSWORD` | Swagger UI 비밀번호 |

### Internal API

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `INTERNAL_API_KEY` | 문제 등록 API 인증용 키. 임의의 문자열 사용 가능 | `my-secret-api-key-1234` |

### 로컬 스토리지

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `SECRET_KEY` | URL 서명에 사용되는 시크릿 키. 임의의 문자열 사용 가능 | `my-secret-key-5678` |

## 선택 환경 변수

기본값이 설정되어 있으나, 필요에 따라서 다른 값으로 변경하여 사용할 수 있습니다.

### 기본 설정

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `ENV` | 실행 환경 | `LOCAL` |
| `STORAGE` | 스토리지 타입 | `LOCAL` |
| `CORS_ORIGINS` | CORS 허용 도메인 | `*` |

### 데이터베이스 (MySQL)

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `MYSQL_USER` | MySQL 사용자명 | `local` |
| `MYSQL_PASSWORD` | MySQL 비밀번호 | `local_password` |
| `MYSQL_HOST` | MySQL 호스트 | `0.0.0.0` |
| `MYSQL_PORT` | MySQL 포트 | `3306` |
| `MYSQL_DB` | 데이터베이스명 | `local` |

### Redis

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `RC_SEED_URL` | Redis 클러스터 URL | `redis:6379` |
| `RC_PASSWORD` | Redis 비밀번호 | `local_password` |
| `RC_TTL` | Redis TTL (초) | `3600` |

### Weaviate (벡터 DB)

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `WEAVIATE_HOST` | Weaviate 호스트 | `localhost` |
| `WEAVIATE_PORT` | Weaviate 포트 | `8081` |
| `PROBLEM_INDEX` | 문제 인덱스명 | `Problem_opensource` |
| `CURRICULUM_INDEX` | 커리큘럼 인덱스명 | `Curriculum_opensource` |

### 모델 서버

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `MODEL_SERVER_GRPC_URL` | 모델 서버 gRPC URL | `edu-model-server:8051` |
| `RESPONSE_MODEL` | 응답 생성 모델 | `hcx-005` |
| `GRPC_PORT` | gRPC 포트 | `8051` |
| `EMBEDDING_TYPE` | 임베딩 타입 | `clovastudio` |

### 로컬 스토리지

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `UPLOAD_DIR` | 파일 업로드 디렉토리 | `static` |
| `URL_EXPIRY_SECONDS` | URL 만료 시간 (초) | `3600` |
| `BASE_URL` | 베이스 URL | `http://localhost:8000/api/v1` |

### 서버 URL

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DATA_SERVER_URL` | 데이터 서버 URL | `http://localhost:8001/api/v1` |
| `BE_SERVER_URL` | 백엔드 서버 URL | `http://localhost:8000/api/v1` |
