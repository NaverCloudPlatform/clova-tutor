# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from chats.domain.chat_message.chat_message import ChatStreamStatus, MessageRole, MessageType
from chats.domain.chat_message.message_content import ChatMessageContent
from chats.domain.chat_message.metadata import SystemHint, ToolInfo
from chats.domain.chat_message.system_content import SystemMessageContent
from chats.domain.chat_problem import ProblemStatus
from common.domain.schema import CommonBase
from problems.presentation.schemas.response_dto import ProblemResponse

# --------------------------------------------------------------------
# Chat 관련 응답 DTO
# --------------------------------------------------------------------

class ChatResponse(BaseModel):
    id: int
    title: str
    subject: str
    has_problem: bool
    has_active_goal: bool
    latest_used_at: datetime


class ActiveGoalResponse(BaseModel):
    id: int
    goal_count: int
    solved_count: int

class ChatDetailResponse(BaseModel):
    id: int
    title: str
    subject: str
    has_problem: bool
    has_active_goal: bool
    active_goal: ActiveGoalResponse | None

# --------------------------------------------------------------------
# ChatProblem 관련 응답 DTO
# --------------------------------------------------------------------

class ChatProblemResponse(BaseModel):
    id: str
    number: int
    status: ProblemStatus
    category: str | None = None
    grade: int
    level: int


class ChatProblemDetailResponse(BaseModel):
    number: int
    status: ProblemStatus
    last_answer: str | None
    is_bookmarked: bool
    problem_info: ProblemResponse


class ChatProblemSubmitResponse(BaseModel):
    is_correct: bool
    active_goal: ActiveGoalResponse | None


# --------------------------------------------------------------------
# ChatMessage 관련 응답 DTO
# --------------------------------------------------------------------

class ChatStreamStatusResponse(BaseModel):
    status: ChatStreamStatus


class MessageAuthor(BaseModel):
    role: MessageRole

class MessageMetadataResponse(BaseModel):
    tools: list[ToolInfo] = []
    system_hints: list[SystemHint] | None = None


class ChatMessageResponse(BaseModel):
    id: int
    chat_id: int
    created_at: datetime
    type: Literal[MessageType.CHAT]
    author: MessageAuthor
    contents: list[ChatMessageContent]
    metadata: MessageMetadataResponse

class SystemMessageResponse(BaseModel):
    id: int
    chat_id: int
    created_at: datetime
    type: Literal[MessageType.SYSTEM]
    author: MessageAuthor
    contents: list[SystemMessageContent]
    metadata: MessageMetadataResponse

MessageResponse = Annotated[
    ChatMessageResponse | SystemMessageResponse,
    Field(discriminator="type"),
]

# SSE 스트리밍 이벤트
class ChatMessageEvent(StrEnum):
    MESSAGE_START = "message_start"
    MESSAGE_DELTA = "message_delta"
    MESSAGE_END = "message_end"

class MessageListResponse(CommonBase):
    data: list[MessageResponse]

class ChatMessageDeltaStream(BaseModel):
    text: str


class StopResponseStatusValue(StrEnum):
    OK = "ok"
class ChatMessageStopResponse(BaseModel):
    status: StopResponseStatusValue

# --------------------------------------------------------------------
# ProblemBookmark 관련 응답 DTO
# --------------------------------------------------------------------

class ProblemDuplicateStatus(StrEnum):
    DUPLICATE = "duplicate"
    UNIQUE = "unique"

class ProblemBookmarkCheckResponse(BaseModel):
    status: ProblemDuplicateStatus


class ProblemBookmarkCreateResponse(BaseModel):
    id: int
    chat_id: int
    problem_id: str
    is_bookmarked: bool
    bookmarked_at: datetime | None

class ProblemBookmarkChatResponse(BaseModel):
    id: int
    has_active_goal: bool


class ProblemBookmarkChatProblemResponse(BaseModel):
    number: int
    status: ProblemStatus
    last_answer: str | None
    problem_info: ProblemResponse

class ProblemBookmarkResponse(BaseModel):
    bookmarked_at: datetime
    chat: ProblemBookmarkChatResponse
    problem: ProblemBookmarkChatProblemResponse
