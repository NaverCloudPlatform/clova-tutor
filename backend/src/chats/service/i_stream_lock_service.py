# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pydantic import BaseModel

from chats.domain.chat_message.chat_message import ChatStreamStatus


class StreamStatusResponse(BaseModel):
    status: ChatStreamStatus
    stream_id: str | None


class IStreamLockService(ABC):
    """
    채팅 스트림 중 락을 위한 인터페이스입니다.
    """

    @asynccontextmanager
    @abstractmethod
    async def acquire_lock(self, chat_id: int, request_id: str, ttl: int | None = None) -> AsyncIterator[bool]:
        """
        Args:
            chat_id (int): 채팅방 ID
            ttl (int): 락 만료 시간 (초)

        Yields:
            bool: 락 획득 성공 여부 (True: 획득, False: 실패)
        """
        yield True

    @abstractmethod
    async def release_lock(
        self,
        chat_id: int
    ) -> None:
        """
        명시적으로 락을 해제합니다.
        """
        ...


    @abstractmethod
    async def check_status(
        self,
        chat_id: int,
        request_id: str | None
    ) -> StreamStatusResponse:
        """
        chat_id 의 키가 존재하는지 확인합니다.
        만약, request_id 까지 넘긴다면 해당 key 값이 request_id와 같은지도 같이 판단하여 응답을 내립니다.
        """
        ...
