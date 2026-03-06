# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from common.service.exceptions import BaseAppException


class ProblemException(BaseAppException):
    """문제 관련 예외의 기본 클래스입니다."""
    default_msg = "문제 오류가 발생했습니다."


class ProblemNotFoundException(ProblemException):
    """문제가 존재하지 않을 때 발생하는 예외"""

    default_msg = "해당 문제를 찾을 수 없습니다."
    def __init__(self, problem_id: str):
        super().__init__(
            data={"problem_id": problem_id}
        )
