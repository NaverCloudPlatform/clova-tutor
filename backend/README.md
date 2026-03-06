# Clova Tutor Backend Server

Clova Tutor 백엔드 서버입니다.

## Requirements

- Docker : 컨테이너화 플랫폼
- uv : Python 의존성 관리 툴

## Docker Compose

Docker Compose를 사용하여 로컬 개발 환경을 시작합니다.

## General Workflow

`./backend/` 경로에서 다음 명령어로 모든 의존성을 설치할 수 있습니다:

```
$ uv sync
```

그 다음 가상 환경을 활성화합니다:

```
$ source .venv/bin/activate
```

## Backend Tests

백엔드 테스트를 실행하려면 다음 명령어를 실행하세요:
```
make test
```
위 명령어는 API 테스트와 유닛 테스트를 모두 실행합니다.  
API 테스트를 위해서는 **TEST DB**가 필요합니다.

`test/confttest.py`에서 본인의 DB 이름으로 변경할 수 있습니다.

```
TEST_DB_NAME = "local"
```

## Migrations

마이그레이션에는 `alembic`을 사용합니다.  
마이그레이션을 적용하려면 다음 명령어를 실행하면 됩니다:

```
make db_apply
```

리비전을 추가하려면 다음과 같이 실행할 수 있습니다:

```
make db_save "add_test"
```