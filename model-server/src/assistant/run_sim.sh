#!/usr/bin/env bash

# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

set -euo pipefail

echo "주의사항: 시뮬레이터 실행 전, setup.sh 파일을 통해 먼저 기본 환경을 설정해주세요. ==="
echo "=== 시뮬레이터 실행 ==="

echo "[1/5] 과목 선택 (--subject)"
read -p "  - 과목을 선택하세요 [eng/math] (기본: eng): " SUBJECT
SUBJECT=${SUBJECT:-eng}

echo "[2/5] 학년 설정 (--grade)"
read -p "  - 학년을 입력하세요 (정수, 기본: 10, 설정 가능: 3, 4, 7, 10): " GRADE
GRADE=${GRADE:-10}

echo "[3/5] 선행학습 차단 옵션 (--block_advanced_learning / --no_block_advanced_learning)"
read -p "  - 선행학습을 차단할까요? [y/N] (기본: N): " BLOCK_ADV
BLOCK_ADV_LOWER=$(printf '%s' "${BLOCK_ADV:-}" | tr '[:upper:]' '[:lower:]')

echo "[4/5] 그래프 출력 옵션 (--draw_graph)"
read -p "  - LangGraph 구조를 그릴까요? [y/N] (기본: N): " DRAW_GRAPH
DRAW_GRAPH_LOWER=$(printf '%s' "${DRAW_GRAPH:-}" | tr '[:upper:]' '[:lower:]')

echo "[5/5] 추가 옵션 (선택)"
read -p "  - 미리 로드할 DB 문제 ID (--db_problem_id), 없으면 엔터: " DB_PROBLEM_ID
read -p "  - 포함할 이미지 URL (--image_url), 없으면 엔터: " IMAGE_URL

echo "  - 추가로 넘길 원시 옵션이 있으면 입력하세요 (예: --test_memory), 없으면 엔터: "
read -r EXTRA_OPTS || true

SIM_OPTS="--subject $SUBJECT --grade $GRADE"

if [ "$BLOCK_ADV_LOWER" = "y" ]; then
  SIM_OPTS+=" --block_advanced_learning"
else
  SIM_OPTS+=" --no_block_advanced_learning"
fi

if [ "$DRAW_GRAPH_LOWER" = "y" ]; then
  SIM_OPTS+=" --draw_graph"
fi

if [ -n "${DB_PROBLEM_ID:-}" ]; then
  SIM_OPTS+=" --db_problem_id \"$DB_PROBLEM_ID\""
fi

if [ -n "${IMAGE_URL:-}" ]; then
  SIM_OPTS+=" --image_url \"$IMAGE_URL\""
fi

if [ -n "${EXTRA_OPTS:-}" ]; then
  SIM_OPTS+=" ${EXTRA_OPTS}"
fi

echo "-> uv run python -m assistant.sim $SIM_OPTS"
eval uv run python -m assistant.sim $SIM_OPTS