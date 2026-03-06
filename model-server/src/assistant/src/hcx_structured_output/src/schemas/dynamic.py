# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/schemas/dynamic.py
import json
import re
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, create_model

from .utils import (
    as_optional,
    coerce_scalar_enum,
    normalize_list_spec,
    parse_nested_object_in_list,
    split_type_list,
    unique_nested_name,
)

_SIMPLE_TYPES = {"str": str, "int": int, "float": float, "bool": bool, "any": Any}
_ALLOWED_EXTRA = {"forbid", "ignore", "allow"}


def _make_base_with_extra(extra: str) -> type[BaseModel]:
    return type("DynamicBase", (BaseModel,), {"model_config": ConfigDict(extra=extra)})


def _parse_type_spec(spec: Any, *, extra: str) -> Any:
    if isinstance(spec, str):
        s = normalize_list_spec(spec.strip())
        if s.startswith("{") and s.endswith("}"):
            try:
                parsed_obj = json.loads(s)
                return _parse_type_spec(parsed_obj, extra=extra)
            except Exception:
                pass

        if s in _SIMPLE_TYPES:
            return _SIMPLE_TYPES[s]
        if s.lower() == "dict":
            return Dict[str, Any]
        if s.lower().startswith("dict[") and s.endswith("]"):
            inner = s[s.index("[") + 1 : -1].strip()
            parts = split_type_list(inner)
            if len(parts) == 2:
                key_type = _parse_type_spec(parts[0], extra=extra)
                value_type = _parse_type_spec(parts[1], extra=extra)
                return Dict[key_type, value_type]  # type: ignore[index]
            else:
                return Dict[str, Any]
        if s.lower().startswith("list[") and s.endswith("]"):
            inner = s[s.index("[") + 1 : -1].strip()
            inner_parsed = parse_nested_object_in_list(inner)
            inner_t = _parse_type_spec(inner_parsed, extra=extra)
            return List[inner_t]  # type: ignore[index]
        if s.lower().startswith("optional[") and s.endswith("]"):
            inner = s[s.index("[") + 1 : -1].strip()
            inner_t = _parse_type_spec(inner, extra=extra)
            return Optional[inner_t]
        if s.lower().startswith("union[") and s.endswith("]"):
            parts = split_type_list(s[s.index("[") + 1 : -1])
            parsed = tuple(_parse_type_spec(p, extra=extra) for p in parts)
            return Union[parsed]
        raise ValueError(
            f"Unsupported type string: {spec!r}. "
            "Supported: 'str', 'int', 'List[str]', 'Optional[int]', 'Union[str, int]', 'dict'"
        )

    if isinstance(spec, dict):
        if set(spec.keys()) == {"enum"}:
            values = spec["enum"]
            if not isinstance(values, list) or not values:
                raise ValueError("enum must be a non-empty list")

            if all(isinstance(v, str) for v in values):
                pattern = r"^(%s)$" % "|".join(re.escape(v) for v in values)
                return Annotated[
                    str, BeforeValidator(coerce_scalar_enum), Field(pattern=pattern)
                ]

            return Literal[tuple(values)]

        fields: Dict[str, tuple] = {
            k: (_parse_type_spec(v, extra=extra), ...) for k, v in spec.items()
        }
        nested_name = unique_nested_name("AnonymousObject", spec)
        base = _make_base_with_extra(extra)
        nested = create_model(nested_name, __base__=base, **fields)
        return nested

    raise ValueError(
        f"Unsupported spec: {spec!r}. Schema must be a string or dictionary."
    )


def _make_field_tuple(spec: Any, *, extra: str) -> tuple:
    if isinstance(spec, dict) and set(spec.keys()) == {"enum"}:
        ann = _parse_type_spec(spec, extra=extra)
        return ann, Field(...)

    if isinstance(spec, str):
        ann = _parse_type_spec(spec, extra=extra)
        return ann, Field(...)

    if isinstance(spec, dict):
        if "enum" in spec and "type" not in spec:
            ann = _parse_type_spec({"enum": spec["enum"]}, extra=extra)
            desc = spec.get("description")
            required = bool(spec.get("required", True))
            if required:
                default_val = ...
            else:
                default_val = spec.get("default", None)
                ann = as_optional(ann)
            return ann, Field(default_val, description=desc)

        typ = spec.get("type", "any")
        ann = _parse_type_spec(typ, extra=extra)

        desc = spec.get("description")
        has_default = "default" in spec
        default_val = spec.get("default", ... if spec.get("required", True) else None)
        required = bool(spec.get("required", not has_default))
        allow_null = bool(spec.get("allow_null", False))

        if required:
            if has_default:
                if default_val is None:
                    ann = as_optional(ann)
                    return ann, Field(..., description=desc)
                else:
                    return ann, Field(default_val, description=desc)
            else:
                if allow_null:
                    ann = as_optional(ann)
                    return ann, Field(..., description=desc)
                else:
                    return ann, Field(..., description=desc)
        else:
            if not has_default:
                default_val = None
            if allow_null or default_val is None:
                ann = as_optional(ann)
            return ann, Field(default_val, description=desc)

    raise ValueError(f"Unsupported field spec: {spec!r}. Must be string or dict.")


def build_model_from_spec(
    name: str,
    spec: Dict[str, Any],
    *,
    extra: str = "forbid",
    model_description: str | None = None,
) -> type[BaseModel]:
    if extra not in _ALLOWED_EXTRA:
        raise ValueError(
            f"extra must be one of {sorted(_ALLOWED_EXTRA)}, got: {extra!r}"
        )
    if not isinstance(spec, dict) or not spec:
        raise ValueError("spec must be a non-empty dict")

    base = _make_base_with_extra(extra)
    fields: Dict[str, tuple] = {}
    for key, field_spec in spec.items():
        ann, fld = _make_field_tuple(field_spec, extra=extra)
        fields[key] = (ann, fld)

    model = create_model(name, __base__=base, **fields)
    if model_description:
        model.__doc__ = model_description
    return model


__all__ = ["build_model_from_spec"]
