# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from pydantic import field_validator

from common.domain.schema import CommonBase


class GoalCreateRequestBody(CommonBase):
    chat_id: int
    goal_count: int

    @field_validator("goal_count")
    @classmethod
    def validate_goal_count(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("목표 숫자는 0보다 커야합니다.")
        return v
