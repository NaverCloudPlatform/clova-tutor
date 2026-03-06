#!/usr/bin/env bash

# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# ------------------------------------------------------------
# 사용법: ./scripts/gen_proto.sh [PROTO_DIR] [OUT_DIR]
#   - 기본값: PROTO_DIR=proto, OUT_DIR=src/grpc_stubs
# ------------------------------------------------------------
set -euo pipefail

PROTO_DIR=${1:-proto}
OUT_DIR=${2:-src/grpc_stubs}

mkdir -p "${OUT_DIR}"

uv run python -m grpc_tools.protoc \
  -I "${PROTO_DIR}" \
  --python_out="${OUT_DIR}" \
  --pyi_out="${OUT_DIR}" \
  --grpc_python_out="${OUT_DIR}" \
  "${PROTO_DIR}/modelchat.proto"

# import 문 수정
if sed --version >/dev/null 2>&1; then   # GNU sed (리눅스)
  sed -i -e 's/^import modelchat_pb2 as modelchat__pb2$/from . import modelchat_pb2 as modelchat__pb2/' \
      "${OUT_DIR}/modelchat_pb2_grpc.py"
else                                     # BSD sed (macOS)
  sed -i '' -e 's/^import modelchat_pb2 as modelchat__pb2$/from . import modelchat_pb2 as modelchat__pb2/' \
      "${OUT_DIR}/modelchat_pb2_grpc.py"
fi

echo "✅ gRPC stubs generated in ${OUT_DIR}"