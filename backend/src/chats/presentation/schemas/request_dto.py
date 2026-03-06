# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from chats.domain.chat_message.message_content import ChatMessageContent
from chats.domain.chat_message.metadata import SystemHint
from problems.domain.problem import ProblemAnswerType


# 채팅방 관련
class ChatCreateRequestBody(BaseModel):
    title: str
    grade: str
    subject: str

    @field_validator("title", mode="before")
    @classmethod
    def validate_test_length(cls, v: str) -> str:
        if len(v) >= 100:
            raise ValueError("title 은 100글자를 넘을 수 없습니다.")
        return v


class ChatTitleUpdateRequestBody(BaseModel):
    title: str

    @field_validator("title", mode="before")
    @classmethod
    def validate_test_length(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("title 은 100글자를 넘을 수 없습니다.")
        if len(v) == 0:
            raise ValueError("title은 비울 수 없습니다.")
        return v


# 채팅 문제 관련

class SingleChoiceAnswer(BaseModel):
    type: Literal[ProblemAnswerType.SINGLE_CHOICE_ANSWER]
    answer: int

class MultipleChoiceAnswer(BaseModel):
    type: Literal[ProblemAnswerType.MULTIPLE_CHOICE_ANSWER]
    answer: list[int]

class SingleShortAnswer(BaseModel):
    type: Literal[ProblemAnswerType.SINGLE_SHORT_ANSWER]
    answer: str

class MultipleShortAnswer(BaseModel):
    type: Literal[ProblemAnswerType.MULTIPLE_SHORT_ANSWER]
    answer: list[str]

QuestionAnswer = Annotated[
    SingleChoiceAnswer | MultipleChoiceAnswer | SingleShortAnswer | MultipleShortAnswer,
    Field(discriminator="type")
]

class ChatProblemSubmitRequestBody(BaseModel):
    answer: QuestionAnswer


# 채팅 메시지 관련
class ChatMessageMetadataRequest(BaseModel):
    system_hints: list[SystemHint] | None = None


class ChatMessageCreateRequestBody(BaseModel):
    contents: list[ChatMessageContent]
    metadata: ChatMessageMetadataRequest


class ChatMessageStopRequestBody(BaseModel):
    chat_id: int


# ProblemBookmark 관련
class ProblemBookmarkCreateRequestBody(BaseModel):
    chat_id: int
    problem_id: str
    is_bookmarked: bool
    bookmarked_at: datetime | None = None
