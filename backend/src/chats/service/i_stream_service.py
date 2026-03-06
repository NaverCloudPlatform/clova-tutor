# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from pydantic import BaseModel

from chats.presentation.schemas.response_dto import ChatMessageDeltaStream, ChatMessageResponse


class ChatStreamResponse(BaseModel):
    seq: int
    is_finish: bool
    content: ChatMessageDeltaStream | ChatMessageResponse


class IChatStreamService(ABC):
    """
    채팅 스트림 데이터를 읽어오는 인터페이스입니다.
    """

    @abstractmethod
    def stream_read_messages(
        self,
        chat_id: int,
        conversation_id: str,
        offset: str | None = None,
        size: int | None = None
    ) -> AsyncIterator[ChatStreamResponse]:
        """
        실시간으로 채팅 스트림을 불러옵니다.
        """
        ...


    @abstractmethod
    async def read_all_messages_from_stream(
        self,
        chat_id: int,
        conversation_id: str,
        offset: str | None = None
    ) -> list[ChatStreamResponse]:
        """
        block_time 없이 현재 존재하는 모든 메시지를 offset 이후부터 불러옵니다.
        """
        ...


    @abstractmethod
    async def add_stream_message(
        self,
        chat_id: int,
        conversation_id: str,
        contents: str,
        is_finish: bool
    ) -> str:
        """
        저장하고, 저장 된 결과 id 를 반환합니다.
        """
        ...

    @abstractmethod
    async def delete_stream_message(
        self,
        chat_id: int,
        conversation_id: str,
        wait_time: int
    ) -> None:
        ...
