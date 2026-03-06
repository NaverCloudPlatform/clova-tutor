#!/usr/bin/env bash

# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SRC_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$SRC_DIR"

echo "=== Edu-Max 초기 실행 셋업 ==="
echo "📍 기준 경로: $SRC_DIR"

# 0. 필수 데이터 파일 경로 입력 및 존재 여부 체크
echo "[0/4] 필수 데이터 파일 경로를 입력해 주세요."
echo "엔터만 치면 기본값(assistant/data/...)를 사용합니다."

declare -a REQUIRED_FILES

read -p "  - eng_grammar_markdown.jsonl 경로 (기본: assistant/data/eng_grammar_markdown.jsonl): " P1
P1=${P1:-assistant/data/eng_grammar_markdown.jsonl}
REQUIRED_FILES+=("$P1")

read -p "  - eng_voca_integrated.jsonl 경로 (기본: assistant/data/eng_voca_integrated.jsonl): " P2
P2=${P2:-assistant/data/eng_voca_integrated.jsonl}
REQUIRED_FILES+=("$P2")

read -p "  - grammar_topic.csv 경로 (기본: assistant/data/grammar_topic.csv): " P3
P3=${P3:-assistant/data/grammar_topic.csv}
REQUIRED_FILES+=("$P3")

read -p "  - opensource_math_course.csv 경로 (기본: assistant/data/opensource_math_course.csv): " P4
P4=${P4:-assistant/data/opensource_math_course.csv}
REQUIRED_FILES+=("$P4")

read -p "  - opensource_math_learning_objectives.csv 경로 (기본: assistant/data/opensource_math_learning_objectives.csv): " P5
P5=${P5:-assistant/data/opensource_math_learning_objectives.csv}
REQUIRED_FILES+=("$P5")

echo "입력된 경로:"
for f in "${REQUIRED_FILES[@]}"; do
  echo "  - $f"
done

MISSING=0
for f in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "  -> 필수 파일이 없습니다: $f"
    MISSING=1
  fi
done

if [ "$MISSING" -eq 1 ]; then
  echo "필수 데이터 파일을 모두 준비한 뒤 다시 실행해 주세요."
  exit 1
fi

mkdir -p assistant/data

if [ "$P1" != "assistant/data/eng_grammar_markdown.jsonl" ]; then
  cp "$P1" assistant/data/eng_grammar_markdown.jsonl
fi

if [ "$P2" != "assistant/data/eng_voca_integrated.jsonl" ]; then
  cp "$P2" assistant/data/eng_voca_integrated.jsonl
fi

if [ "$P3" != "assistant/data/grammar_topic.csv" ]; then
  cp "$P3" assistant/data/grammar_topic.csv
fi

if [ "$P4" != "assistant/data/opensource_math_course.csv" ]; then
  cp "$P4" assistant/data/opensource_math_course.csv
fi

if [ "$P5" != "assistant/data/opensource_math_learning_objectives.csv" ]; then
  cp "$P5" assistant/data/opensource_math_learning_objectives.csv
fi

# 1. 가상환경 활성화
if [ -d "../.venv" ]; then
  echo "[1/4] .venv 활성화"
  # 프로젝트 루트의 venv 활성화
  source ../.venv/bin/activate
else
  echo "[1/4] ../.venv가 없어 uv로 새로 생성합니다."
  # uv로 가상환경 생성 및 패키지 설치 (프로젝트 루트에서 실행)
  (
    cd .. && uv sync
  )
  if [ ! -d "../.venv" ]; then
    echo "uv sync 후에도 ../.venv 디렉토리를 찾을 수 없습니다. uv 설정을 확인해 주세요."
    exit 1
  fi
  echo "[1/4] .venv 활성화"
  source ../.venv/bin/activate
fi

# 2. api_info.yaml 경로 확인
if [ -f "assistant/api_info.yaml" ]; then
  echo "[2/4] api_info.yaml 발견: assistant/api_info.yaml"
  API_INFO_PATH="assistant/api_info.yaml"
else
  echo "[2/4] api_info.yaml 파일이 없습니다. 다른 경로를 입력해 주세요."
  read -p "  - api_info.yaml 경로: " API_INFO_PATH
  if [ -z "$API_INFO_PATH" ] || [ ! -f "$API_INFO_PATH" ]; then
    echo "  -> 유효한 api_info.yaml 파일을 찾을 수 없습니다: $API_INFO_PATH"
    exit 1
  fi
fi

mkdir -p assistant
if [ "$API_INFO_PATH" != "assistant/api_info.yaml" ]; then
  cp "$API_INFO_PATH" assistant/api_info.yaml
fi
API_INFO_PATH="assistant/api_info.yaml"

# 3. vector index 생성 여부 확인
echo "[3/4] 벡터 인덱스 생성 옵션 설정"

read -p "Math Curriculum 인덱스를 생성할까요? (y/N): " CREATE_CURR
CREATE_CURR_LOWER=$(printf '%s' "$CREATE_CURR" | tr '[:upper:]' '[:lower:]')
if [ "$CREATE_CURR_LOWER" = "y" ]; then
  read -p "  - Curriculum 인덱스 이름 (기본값: Curriculum_opensource): " CURR_INDEX
  CURR_INDEX=${CURR_INDEX:-Curriculum_opensource}

  DEFAULT_CSV="assistant/data/opensource_math_course.csv"
  read -p "  - Curriculum CSV 경로 (기본값: $DEFAULT_CSV): " CURR_CSV
  CURR_CSV=${CURR_CSV:-$DEFAULT_CSV}

  if [ ! -f "$CURR_CSV" ]; then
    echo "  -> 파일을 찾을 수 없습니다: $CURR_CSV"
    exit 1
  fi
  echo "  -> 설정된 경로: $CURR_CSV"

  echo "  -> python -m assistant.src.client.vector create $CURR_INDEX $CURR_CSV"
  python -m assistant.src.client.vector create "$CURR_INDEX" "$CURR_CSV"
fi

read -p "Problem 인덱스를 생성할까요? (y/N): " CREATE_PROB
CREATE_PROB_LOWER=$(printf '%s' "$CREATE_PROB" | tr '[:upper:]' '[:lower:]')
if [ "$CREATE_PROB_LOWER" = "y" ]; then
  read -p "  - Problem 인덱스 이름 (기본값: Problem_opensource): " PROB_INDEX
  PROB_INDEX=${PROB_INDEX:-Problem_opensource}

  DEFAULT_PROB_CSV="assistant/data/opensource_problem.csv"
  read -p "  - Problem CSV 경로 (기본값: $DEFAULT_PROB_CSV): " PROB_CSV
  PROB_CSV=${PROB_CSV:-$DEFAULT_PROB_CSV}
  if [ ! -f "$PROB_CSV" ]; then
    echo "  -> 파일을 찾을 수 없습니다: $PROB_CSV"
    exit 1
  fi

  echo "  -> 설정된 경로: $PROB_CSV"

  echo "  -> python -m assistant.src.client.vector create $PROB_INDEX $PROB_CSV"
  python -m assistant.src.client.vector create "$PROB_INDEX" "$PROB_CSV"
fi