# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/schemas/utils.py
import hashlib
import json
from typing import Any, Optional, Union, get_args, get_origin


def normalize_list_spec(s: str) -> str:
    s = s.strip()
    if s.startswith("List[") and s.endswith("]"):
        return "List[" + s[5:-1].strip() + "]"
    return s


def split_type_list(s: str) -> list[str]:
    parts, buf, depth = [], [], 0
    for ch in s:
        if ch in "[(":
            depth += 1
            buf.append(ch)
        elif ch in "])":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf.clear()
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def parse_nested_object_in_list(inner_spec: str) -> Any:
    inner_spec = inner_spec.strip()
    if inner_spec.startswith("{") and inner_spec.endswith("}"):
        try:
            return json.loads(inner_spec)
        except json.JSONDecodeError:
            pass
    return inner_spec


def unique_nested_name(prefix: str, spec: Any) -> str:
    h = hashlib.sha1(
        json.dumps(spec, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:8]
    return f"{prefix}_{h}"


def as_optional(ann):
    if get_origin(ann) is Union and type(None) in get_args(ann):
        return ann
    return Optional[ann]


def coerce_scalar_enum(v):
    # enum: ["a","b",...]에서 모델이 리스트/콤마로 줄 때 첫 토큰만 취함
    if isinstance(v, list):
        for tok in v:
            if isinstance(tok, str) and tok.strip():
                return tok.strip()
        return v[0] if v else v
    if isinstance(v, str) and "," in v:
        return v.split(",")[0].strip()
    return v
