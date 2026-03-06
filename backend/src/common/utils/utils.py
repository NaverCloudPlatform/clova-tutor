# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from zoneinfo import ZoneInfo


def attach_timezone(dt: datetime, timezone: str = "Asia/Seoul") -> datetime:
    """
    주어진 datetime 객체에 타임존 정보를 추가하여 반환합니다.
    """
    if dt.tzinfo is not None:
        return dt.astimezone(ZoneInfo(timezone))
    return dt.replace(tzinfo=ZoneInfo(timezone), microsecond=0)
