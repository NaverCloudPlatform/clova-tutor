# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from typing import Annotated, ClassVar

from typing_extensions import Doc

from chats.domain.chat_message.message_content import ChatMessageContent
from chats.domain.chat_message.metadata import ChatMessageMetadata
from chats.domain.chat_message.system_content import SystemMessageContent
from common.domain.schema import CommonBase, IntIdMixin


class MessageType(StrEnum):
    """메시지의 타입을 정의하는 열거형 클래스입니다.

    Attributes:
        CHAT: 일반 채팅 메시지
        SYSTEM: 시스템 메시지
    """

    CHAT = "chat"
    SYSTEM = "system"


class MessageRole(StrEnum):
    """메시지 작성자의 역할을 정의하는 열거형 클래스입니다.

    Attributes:
        USER: 사용자가 작성한 메시지
        ASSISTANT: AI 어시스턴트가 작성한 메시지
        SYSTEM: 시스템이 작성한 메시지
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatStreamStatus(StrEnum):
    IS_STREAMING = "IS_STREAMING"
    COMPLETE = "COMPLETE"

class ChatMessage(CommonBase,IntIdMixin):
    FIELD_CHAT_ID: ClassVar[str] = "chat_id"
    FIELD_TYPE: ClassVar[str] = "type"
    FIELD_ROLE: ClassVar[str] = "role"
    FIELD_CONTENT: ClassVar[str] = "content"
    FIELD_META_DATA: ClassVar[str] = "meta_data"

    chat_id: Annotated[int, Doc("채팅방 ID 입니다.")]

    type: Annotated[MessageType, Doc("채팅 메시지의 타입입니다. 채팅 / 시스템 메시지로 구분됩니다.")]
    role: Annotated[MessageRole, Doc("채팅 메시지 주체의 역할입니다. 사용자 / 모델 / 시스템 으로 구분됩니다.")]

    content: Annotated[Sequence[ChatMessageContent | SystemMessageContent], Doc("메시지 내용입니다.")]
    meta_data: Annotated[ChatMessageMetadata, Doc("채팅 메시지 관련 메타데이터입니다.")]


class ChatMessageWithDate(ChatMessage):
    FIELD_CREATED_AT: ClassVar[str] = "created_at"

    created_at: Annotated[datetime, Doc("생성 날짜입니다.")]
