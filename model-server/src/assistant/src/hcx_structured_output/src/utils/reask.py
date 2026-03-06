# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from enum import Enum
from typing import Any, Callable, List, Optional, Union, get_args, get_origin

from pydantic import BaseModel, ValidationError

_CreateFn = Callable[..., Any]


def _unwrap_optional(tp: Any) -> Any:
    """Optional[T] → T"""
    if get_origin(tp) is Union:
        args = [a for a in get_args(tp) if a is not type(None)]  # noqa: E721
        if len(args) == 1:
            return args[0]
    return tp


def _type_to_str(tp: Any) -> str:
    tp = _unwrap_optional(tp)

    # Pydantic BaseModel
    if isinstance(tp, type) and issubclass(tp, BaseModel):
        return tp.__name__

    # Enum
    if isinstance(tp, type) and issubclass(tp, Enum):
        vals = [e.value for e in tp]  # type: ignore[attr-defined]
        return f"Enum{vals}"

    origin = get_origin(tp)
    args = get_args(tp)

    if origin in (list, List):
        inner = _type_to_str(args[0]) if args else "Any"
        return f"List[{inner}]"
    if origin in (dict, Dict := dict):
        k = _type_to_str(args[0]) if args else "Any"
        v = _type_to_str(args[1]) if len(args) > 1 else "Any"
        return f"Dict[{k}, {v}]"

    if tp in (str,):
        return "string"
    if tp in (int,):
        return "integer"
    if tp in (float,):
        return "number"
    if tp in (bool,):
        return "boolean"
    if tp in (Any,):
        return "any"

    return getattr(tp, "__name__", str(tp))


def _default_for_type(tp: Any) -> Any:
    tp = _unwrap_optional(tp)

    if isinstance(tp, type) and issubclass(tp, BaseModel):
        return _skeleton_from_model(tp)

    if isinstance(tp, type) and issubclass(tp, Enum):
        for e in tp:  # type: ignore[attr-defined]
            return e.value
        return None

    origin = get_origin(tp)
    args = get_args(tp)
    if origin in (list, List):
        return []
    if origin in (dict, Dict := dict):
        return {}

    if tp in (str,):
        return ""
    if tp in (int, float):
        return 0
    if tp in (bool,):
        return False

    # If unknown, return empty object (safe)
    return {}


def _skeleton_from_model(model: type[BaseModel]) -> dict:
    """Model's field order preserved Skeleton JSON"""
    out = {}
    for name, field in model.model_fields.items():  # pydantic v2
        ann = field.annotation
        out[name] = _default_for_type(ann)
    return out


def _required_keys(model: type[BaseModel]) -> List[str]:
    req = []
    for name, field in model.model_fields.items():
        if field.is_required():
            req.append(name)
    return req


def _types_map(model: type[BaseModel]) -> List[str]:
    pairs = []
    for name, field in model.model_fields.items():
        pairs.append(f"{name}: {_type_to_str(field.annotation)}")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Error → Reask Instruction
# ─────────────────────────────────────────────────────────────────────────────


def _format_errors(err: Exception, lang: str = "ko") -> str:
    """ValidationError를 읽기 쉬운 불릿으로 요약"""
    if not isinstance(err, ValidationError):
        return str(err)

    lines: List[str] = []
    for e in err.errors():
        etype = e.get("type") or ""
        loc = ".".join(map(str, e.get("loc", []))) or "(root)"
        msg = e.get("msg") or ""

        hint = ""
        # Add hints for frequently seen types
        if etype == "missing":
            hint = "→ 필수 필드를 포함하세요."
        elif etype.endswith("_type"):
            hint = "→ 타입을 점검하세요."
        elif "extra_forbidden" in etype or "extra" in msg.lower():
            hint = "→ 스키마에 없는 추가 키를 제거하세요."
        elif "json_invalid" in etype or "Invalid JSON" in msg:
            hint = "→ JSON 문법 오류(쉼표/괄호/따옴표)를 고치세요."
        elif "json_type" in etype and "list" in msg.lower():
            hint = "→ 배열이 아닌 단일 객체를 출력하세요."

        lines.append(f"- {loc}: {msg} {hint}".rstrip())

    return "\n".join(lines) or str(err)


def _ko_header(model: Optional[type[BaseModel]]) -> str:
    base = [
        "이전 응답이 **스키마 유효성 검사**를 통과하지 못했습니다.",
        "아래 지시를 따라 **'주어진 Schema에 맞는 JSON 객체'**만 다시 출력하세요.",
        "코드블록 금지, JSON 외 모든 텍스트 금지, 배열([]) 금지.",
    ]
    if model:
        req = ", ".join(_required_keys(model)) or "(없음)"
        types = "\n".join(f"  - {t}" for t in _types_map(model))
        base += [
            "",
            f"필수 키: {req}",
            "필드 타입:",
            types,
        ]
    return "\n".join(base)


def _en_header(model: Optional[type[BaseModel]]) -> str:
    base = [
        "Your previous response failed **schema validation**.",
        "Follow the instructions and return **exactly ONE JSON object**.",
        "No code fences, no extra text, no arrays ([]).",
    ]
    if model:
        req = ", ".join(_required_keys(model)) or "(none)"
        types = "\n".join(f"  - {t}" for t in _types_map(model))
        base += [
            "",
            f"Required keys: {req}",
            "Field types:",
            types,
        ]
    return "\n".join(base)


def _ko_footer(model: Optional[type[BaseModel]]) -> str:
    if not model:
        return ""
    import json

    skeleton = _skeleton_from_model(model)
    # Note: No code fences, just a reference example
    return "\n".join(
        [
            "",
            "참고용 스켈레톤(값은 예시, 그대로 복붙하지 말고 실제 값으로 채우세요):",
            json.dumps(skeleton, ensure_ascii=False, indent=2),
        ]
    )


def _en_footer(model: Optional[type[BaseModel]]) -> str:
    if not model:
        return ""
    import json

    skeleton = _skeleton_from_model(model)
    return "\n".join(
        [
            "",
            "Skeleton example (fill with actual values; do NOT copy verbatim):",
            json.dumps(skeleton, ensure_ascii=False, indent=2),
        ]
    )


def err_to_reask(
    err: Exception,
    model: Optional[type[BaseModel]] = None,
    lang: str = "ko",
) -> str:
    """
    Create more specific reask instruction:
    - Error summary (field path, type, hint)
    - (Optional) Model-based required keys/types
    - (Optional) Skeleton JSON example
    """
    details = _format_errors(err, lang=lang)

    if lang.lower().startswith("ko"):
        header = _ko_header(model)
        footer = _ko_footer(model)
        return "\n".join([header, "", "Errors:", details, footer]).strip()

    header = _en_header(model)
    footer = _en_footer(model)
    return "\n".join([header, "", "Errors:", details, footer]).strip()


# ─────────────────────────────────────────────────────────────────────────────
# 1 call & manual retry loop (no change, just pass model to err_to_reask)
# ─────────────────────────────────────────────────────────────────────────────


def call_once(
    create_fn: _CreateFn,
    *,
    model: str,
    messages: List[dict],
    temperature: float,
    response_model: type[BaseModel],
    run_id: Optional[str],
    debug: bool,
) -> BaseModel:
    # Instructor internal retry is disabled (=1)
    return create_fn(
        model=model,
        messages=messages,
        temperature=temperature,
        response_model=response_model,
        max_retries=1,
        _run_id=run_id,
        _debug=debug,
    )


def manual_retry_loop(
    create_fn: _CreateFn,
    *,
    model: str,
    base_messages: List[dict],
    temperature: float,
    response_model: type[BaseModel],
    max_retries: int,
    run_id: Optional[str],
    debug: bool,
    language: str = "ko",
) -> BaseModel:
    messages = list(base_messages)

    for attempt in range(1, max_retries + 1):
        try:
            return call_once(
                create_fn,
                model=model,
                messages=messages,
                temperature=temperature,
                response_model=response_model,
                run_id=run_id,
                debug=debug,
            )
        except Exception as e:
            # Error → Reask prompt creation (with model info)
            reask_text = err_to_reask(e, model=response_model, lang=language)
            messages = list(messages) + [{"role": "user", "content": reask_text}]
            if attempt == max_retries:
                raise
