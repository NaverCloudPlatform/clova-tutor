# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any
from uuid import UUID

from common.service.exceptions import BaseAppException


class UserException(BaseAppException):
    """사용자 관련 예외의 기본 클래스입니다.

    Attributes:
        default_message (str): 예외 메시지
    """
    default_msg = "유저 오류가 발생했습니다."


class UserNotFoundException(UserException):
    """사용자를 찾을 수 없을 때 발생하는 예외입니다.

    Attributes:
        user_id (UUID): 찾을 수 없는 사용자의 ID
    """

    default_msg = "해당 ID의 유저를 찾을 수 없습니다."

    def __init__(self, user_id: UUID):
        super().__init__(
            data={"user_id": str(user_id)}
        )

class UserUnknownConceptNotFoundException(UserException):
    default_msg = "요청된 조건(유저, 과목, 핵심 개념)에 해당하는 데이터를 찾을 수 없습니다."
    def __init__(
        self,
        user_id: UUID | None = None,
        subject: str | None = None,
        key_concept: str | None = None,
    ) -> None:
        exception_data: dict[str, Any] = {}
        if user_id is not None:
            exception_data["user_id"] = str(user_id)
        if subject is not None:
            exception_data["subject"] = subject
        if key_concept is not None:
            exception_data["key_concept"] = key_concept

        super().__init__(
            data=exception_data
        )
