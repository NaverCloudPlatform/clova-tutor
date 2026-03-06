# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from common.domain.schema import CommonBase


class GoalResponse(CommonBase):
    id: int
    goal_count: int
    solved_count: int
