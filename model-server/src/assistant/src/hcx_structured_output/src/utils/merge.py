# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/utils/merge.py
from typing import Any, Dict, List, Optional, get_args, get_origin

from pydantic import BaseModel


def _unwrap_optional(t: Any) -> Any:
    """Unwrap Optional[T] or Union[T, NoneType] to T."""
    origin = get_origin(t)
    if origin is None:
        return t
    if origin is __import__("typing").Union:
        args = tuple(a for a in get_args(t) if a is not type(None))
        return args[0] if len(args) == 1 else t
    return t


def _is_empty(x: Any) -> bool:
    return x is None or x == "" or x == [] or x == {}


def _default_merge_strategy(field_type: Any, left: Any, right: Any) -> Any:
    """Default strategy for merging two values of the same field."""
    if _is_empty(left):
        return right
    if _is_empty(right):
        return left

    t = _unwrap_optional(field_type)
    origin = get_origin(t)

    if origin in (list, List):
        return (left or []) + (right or [])

    if t is str:
        l = (left or "").rstrip()
        r = (right or "").lstrip()
        if not l:
            return r
        if not r:
            return l
        return l + "\n\n" + r

    # Dictionary merging (right overwrites left)
    if origin in (dict, Dict):
        merged = dict(left or {})
        merged.update(right or {})
        return merged

    return left


def merge_pydantic_models(
    models: List[BaseModel],
    response_model: type[BaseModel],
    *,
    custom_strategy: Optional[Dict[str, Any]] = None,
) -> BaseModel:
    custom_strategy = custom_strategy or {}
    if not models:
        raise ValueError("models is empty")
    if len(models) == 1:
        return models[0]

    merged: Dict[str, Any] = {}
    hints = response_model.model_fields

    for name, field in hints.items():
        strat = custom_strategy.get(name)
        if strat is not None and not callable(strat):
            raise TypeError(f"custom_strategy['{name}'] must be callable")
        acc = None
        ftype = field.annotation
        for m in models:
            val = getattr(m, name, None)
            acc = strat(acc, val) if strat else _default_merge_strategy(ftype, acc, val)
        merged[name] = None if _is_empty(acc) else acc

    return response_model.model_validate(merged)
