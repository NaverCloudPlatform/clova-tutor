# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from enum import StrEnum
from typing import Annotated, ClassVar
from uuid import UUID

from typing_extensions import Doc

from common.domain.schema import CommonBase, IntIdMixin
from problems.domain.problem import SubjectEnum


class GoalStatus(StrEnum):
    COMPLETED = "COMPLETED"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"

class Goal(CommonBase, IntIdMixin):
    FIELD_SUBJECT: ClassVar[str] = "subject"
    FIELD_USER_ID: ClassVar[str] = "user_id"
    FIELD_CHAT_ID: ClassVar[str] = "chat_id"
    FIELD_GOAL_COUNT: ClassVar[str] = "goal_count"
    FIELD_SOLVED_COUNT: ClassVar[str] = "solved_count"
    FIELD_FINISHED_AT: ClassVar[str] = "finished_at"
    FIELD_STATUS: ClassVar[str] = "status"

    subject: Annotated[SubjectEnum,Doc("채팅방 과목이름 (필터링을 위해 존재)")]
    user_id: Annotated[UUID,Doc("유저 id. 유저별 목표 달성 수를 위해 존재")]
    chat_id: Annotated[int, Doc("채팅 id. 채팅에 해당하는 목표")]
    goal_count: Annotated[int,Doc("최종 목표 문제 수")]
    solved_count: Annotated[int, Doc("현재까지 푼 문제 수")] = 0
    finished_at: Annotated[datetime | None, Doc("목표 달성이 언제 끝났는지")] = None
    status: Annotated[GoalStatus, Doc("현재 목표 상태를 나타냅니다.") ]
