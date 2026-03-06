# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from common.service.exceptions import BaseAppException


class GoalException(BaseAppException):
    default_msg = "목표 기록 관련 에러가 발생했습니다."


class NotFoundGoalException(GoalException):
    default_msg = "해당 목표 기록을 찾을 수 없습니다."
    def __init__(self, goal_id: int | None = None):
        super().__init__(
            data={"goal_id" : goal_id}
        )


class InvalidGoalValueExeception(GoalException):
    default_msg = "목표 관련 수치를 초과하였습니다."

    def __init__(self, msg: str | None = None):
        super().__init__(msg=msg)
