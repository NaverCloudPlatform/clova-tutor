# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import base64

from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel, Field
from pydantic_core import ValidationError, from_json, to_json

T = TypeVar("T")

class CursorPaginateParams(BaseModel):
    # 커서 기반 페이지네이션 입니다.
    # cursor의 응답은 id를 기준으로 합니다.
    cursor: str | None = None
    size: int = Field(10,ge=1,le=100)


class CursorPaginateResponse(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None


def encode_cursor(cursor_data: dict[str, Any]) -> str | None:
    """
    딕셔너리 형태의 여러 필드를 하나의 커서 문자열로 인코딩합니다.
    (내부적으로 JSON 및 Base64를 사용)
    """
    try:
        json_bytes = to_json(cursor_data)
        return base64.urlsafe_b64encode(json_bytes).decode('utf-8')
    except ValidationError:
        return None


def decode_cursor(cursor_str: str) -> dict[str, Any]:
    """
    인코딩된 커서 문자열에서 필드 딕셔너리를 디코딩합니다.
    디코딩 후 datetime 문자열은 그대로 문자열로 반환됩니다.
    """
    try:
        # Base64 URL Safe 디코딩
        decoded_bytes = base64.urlsafe_b64decode(cursor_str)

        # JSON 문자열을 딕셔너리로 변환
        cursor_data = from_json(decoded_bytes)

        return cast(dict[str,Any], cursor_data)
    except (ValueError, TypeError, ValidationError):
        return {}

