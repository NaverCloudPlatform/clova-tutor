# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from goals.service.exceptions import GoalException


class ActiveGoalExistException(GoalException):
    default_msg = "이미 해당 채팅방에 Active 목표가 존재합니다."
