# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any


class BaseAppException(Exception):
    def __init__(
        self,
        msg: str | None = None,
        *,
        kind: str | None = None,
        data: dict[str, Any] | None = None,
    ):
        # msg가 없으면 subclass에 정의된 default_msg 사용
        default_msg = getattr(self, "default_msg", None)
        final_msg = msg or default_msg or self.__class__.__name__

        super().__init__(final_msg)
        self.msg = final_msg
        self.kind = kind or self.__class__.__name__ # 기본은 클래스이름.
        self.data = data or {}
