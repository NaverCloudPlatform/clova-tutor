# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/schemas/primitives.py
from typing import Any, Dict, List

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    conlist,
    field_validator,
    model_validator,
)


class BilingualSegment(BaseModel):
    en: str = Field(min_length=1)
    ko: str = Field(min_length=1)


def _normalize_spaces(s: Any) -> str:
    if s is None:
        return ""
    return " ".join(str(s).split()).strip()


def _normalize_segment_items(items: Any) -> List[Dict[str, str]]:
    if not isinstance(items, list):
        return []
    fixed: List[Dict[str, str]] = []
    for seg in items:
        en_raw = seg["en"] if isinstance(seg, dict) else getattr(seg, "en", "")
        ko_raw = seg["ko"] if isinstance(seg, dict) else getattr(seg, "ko", "")
        en = _normalize_spaces(en_raw)
        ko = _normalize_spaces(ko_raw)
        if en and ko:
            fixed.append({"en": en, "ko": ko})
    return fixed


class _NormalizedSegmentsMixin(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def _normalize(cls, data):
        items = (
            data["segments"] if isinstance(data, dict) and "segments" in data else data
        )
        return {"segments": _normalize_segment_items(items)}

    @field_validator("segments", check_fields=False)
    @classmethod
    def _non_empty_fields(cls, segs: List[BilingualSegment]):
        if not segs:
            raise ValueError("segments is empty.")
        for i, s in enumerate(segs):
            if not s.en.strip():
                raise ValueError(f"segments[{i}].en is empty.")
            if not s.ko.strip():
                raise ValueError(f"segments[{i}].ko is empty.")
        return segs


class Segments(_NormalizedSegmentsMixin):
    segments: conlist(BilingualSegment, min_length=1)


class AtLeastOneSegments(_NormalizedSegmentsMixin):
    segments: conlist(BilingualSegment, min_length=1)


class SingleKeyModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


__all__ = ["BilingualSegment", "Segments", "AtLeastOneSegments", "SingleKeyModel"]
