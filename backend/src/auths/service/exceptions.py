# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any

from common.service.exceptions import BaseAppException


class AuthException(BaseAppException):
    default_msg = "인증 관련 에러 발생 했습니다."

class HeaderNotExistException(AuthException):
    default_msg = "X-User-Id header가 존재하지 않습니다."


class HeaderTypeNotMatchException(AuthException):
    default_msg = "잘못된 X-User-Id header 값입니다."
    def __init__(self, user_id: Any) -> None:
        super().__init__(
            data= {
                "user_id" : user_id
            }
        )
