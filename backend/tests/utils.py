# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any


def assert_structure(obj: Any, skeleton: Any) -> None:
    # dict 구조 검사
    if isinstance(skeleton, dict):
        # 키 템플릿 방식
        if len(skeleton) == 1 and next(iter(skeleton)) not in obj:
            template = next(iter(skeleton.values()))
            for v in obj.values():
                assert_structure(v, template)
        else:
            for k, v in skeleton.items():
                assert k in obj, f"키 누락: {k}"
                assert_structure(obj[k], v)
    # list 구조 검사
    elif isinstance(skeleton, list):
        assert isinstance(obj, list), "리스트여야 함"
        if skeleton:
            for item in obj:
                assert_structure(item, skeleton[0])
    # leaf 노드: 키 존재만 보장
    else:
        return
