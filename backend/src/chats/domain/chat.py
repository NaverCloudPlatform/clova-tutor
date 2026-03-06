# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime
from typing import Annotated, ClassVar

from typing_extensions import Doc

from common.domain.schema import CommonBase, IntIdMixin
from problems.domain.problem import GradeEnum, SubjectEnum


class Chat(CommonBase, IntIdMixin):
    FIELD_USER_ID: ClassVar[str] = "user_id"
    FIELD_TITLE: ClassVar[str] = "title"
    FIELD_GRADE: ClassVar[str] = "grade"
    FIELD_SUBJECT: ClassVar[str] = "subject"
    FIELD_LATEST_USED_AT: ClassVar[str] = "latest_used_at"

    title: Annotated[str, Doc("채팅 세션의 제목 (예: '수학 문제 풀이 대화')")]
    user_id: Annotated[uuid.UUID, Doc("채팅을 생성한 사용자 식별자 (UUID)")]
    grade: Annotated[GradeEnum, Doc("대상 학년 (예: GRADE_1 ~ GRADE_12)")]
    subject: Annotated[SubjectEnum, Doc("채팅 주제 과목 (예: MATH, SCIENCE)")]
    latest_used_at: Annotated[datetime, Doc("해당 채팅이 마지막으로 사용된 시각 (최근 대화 정렬용)")]


class ChatDetail(Chat):
    FIELD_HAS_PROBLEM: ClassVar[str] = "has_problem"
    FIELD_HAS_ACTIVE_GOAL: ClassVar[str] = "has_active_goal"

    has_problem: Annotated[bool, Doc("채팅에 문제 존재 여부")]
    has_active_goal: Annotated[bool, Doc("채팅에 활성화된 목표 존재 여부")]
