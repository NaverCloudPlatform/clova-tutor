###############################################################################
# 1. builder stage
#    ─ Python 의존성 설치 후 /edu/app 에 애플리케이션 코드 복사
###############################################################################
FROM python:3.11.5 AS builder

USER root

RUN apt-get update && apt-get install -y vim less

# 파이썬 패키지 설치
COPY --from=ghcr.io/astral-sh/uv:0.8.2 /uv /uvx /bin/

WORKDIR /edu

COPY ./pyproject.toml /edu/pyproject.toml
COPY ./uv.lock /edu/uv.lock

RUN uv sync --frozen --no-cache
# 애플리케이션 코드 복사

COPY ./src ./app
COPY ./proto ./proto
COPY ./scripts/gen_proto.sh ./scripts/gen_proto.sh

RUN chmod +x ./scripts/gen_proto.sh && \
    ./scripts/gen_proto.sh proto app/grpc_stubs

###############################################################################
# 2. runtime stage (최종 이미지)
###############################################################################
FROM python:3.11.5

USER root
RUN apt-get update && apt-get install -y vim less

# builder 단계에서 설치한 파이썬 패키지와 애플리케이션 코드 가져오기
COPY --from=builder /usr/local /usr/local
COPY --from=builder /edu/.venv /edu/.venv
COPY --from=builder /edu/app /edu/app

# 실행 디렉토리 지정
WORKDIR /edu/app
