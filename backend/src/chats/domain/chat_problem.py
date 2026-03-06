# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from enum import StrEnum
from typing import Annotated, ClassVar
from uuid import UUID

from typing_extensions import Doc

from chats.domain.chat import ChatDetail
from common.domain.schema import CommonBase, IntIdMixin
from problems.domain.problem import Problem


class ProblemStatus(StrEnum):
    UNSOLVED = "풀지 않음"
    CORRECT = "정답"
    WRONG = "오답"
    REVIEWED = "복습 완료"


class ChatProblem(CommonBase, IntIdMixin):
    FIELD_CHAT_ID: ClassVar[str] = "chat_id"
    FIELD_PROBLEM_ID: ClassVar[str] = "problem_id"
    FIELD_USER_ID: ClassVar[str] = "problem_id"
    FIELD_STATUS: ClassVar[str] = "status"
    FIELD_LAST_ANSWER: ClassVar[str] = "last_answer"
    FIELD_IS_BOOKMARKED: ClassVar[str] = "is_bookmarked"
    FIELD_BOOKMARKED_AT: ClassVar[str] = "bookmarked_at"

    chat_id: Annotated[int, Doc("채팅방 ID")]
    problem_id: Annotated[str, Doc("문제 ID")]
    user_id: Annotated[UUID, Doc("사용자 ID")]
    number: Annotated[int, Doc("채팅방 내의 문제 번호")]

    status: Annotated[ProblemStatus, Doc("문제 풀이 상태")]
    last_answer: Annotated[str | None, Doc("마지막 오답/답변")]

    is_bookmarked: Annotated[bool, Doc("북마크 여부")]
    bookmarked_at: Annotated[datetime | None, Doc("북마크 시점")]

class ChatProblemDetail(ChatProblem):
    FIELD_PROBLEM: ClassVar[str] = "problem"

    problem: Annotated[Problem, Doc("문제 상세 정보입니다.")]

class ChatProblemWithChatDetailAndWithProblem(ChatProblem):
    FIELD_PROBLEM: ClassVar[str] = "problem"
    FIELD_CHAT_DETAIL: ClassVar[str] = "chat"

    problem: Annotated[Problem, Doc("문제 상세 정보입니다.")]
    chat: Annotated[ChatDetail, Doc("채팅방 관련 상세 정보입니다. / 활성 목표 존재 여부 파악")]
