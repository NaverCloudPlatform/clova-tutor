# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
import logging

from collections.abc import AsyncIterator
from typing import Any

from fastapi import Depends
from pydantic import TypeAdapter

from chats.presentation.schemas.response_dto import ChatMessageDeltaStream, ChatMessageResponse
from chats.service.i_stream_service import ChatStreamResponse, IChatStreamService
from common.infra.redis import RedisManager, get_redis_client
from common.utils.logger import register_internal_service_log

CHAT_MESSAGES_KEY = "chat:messages"
DEFAULT_BLOCK_TIME = 60 * 1000
DEFAULT_SIZE = 100

class RedisStreamService(IChatStreamService):
    def __init__(
        self,
        redis_client: RedisManager
    ):
        self.redis_client = redis_client
        self._ta: TypeAdapter[ChatMessageDeltaStream | ChatMessageResponse] = TypeAdapter(ChatMessageDeltaStream | ChatMessageResponse)

    async def stream_read_messages(
        self,
        chat_id: int,
        conversation_id: str,
        offset: str | None = None,
        size: int | None = None
    ) -> AsyncIterator[ChatStreamResponse]:

        current_id = offset
        if current_id is None:
            current_id = "0-0" # 시작

        if size is None:
            size = DEFAULT_SIZE

        stream_key = f"{CHAT_MESSAGES_KEY}:{chat_id}:{conversation_id}"
        block_time = DEFAULT_BLOCK_TIME

        seq = 1

        while True:
            try:
                response = await self.redis_client.xread(
                    {stream_key : current_id},
                    count=size,
                    block=block_time
                )
            except Exception as e:
                register_internal_service_log(
                    f"Redis XREAD error during fallback: {e}",
                    level=logging.ERROR
                )
                raise # Redis 에러 전파

            if not response or not response[0][1]:
                # 타임아웃 또는 스트림에 메시지 없는 경우
                break

            stream_messages: list[tuple[str, dict[str, Any]]] = response[0][1]
            last_stream_id: str | None = None

            for stream_id, fields_dict in stream_messages:
                last_stream_id = stream_id

                json_data = fields_dict.get("data", None)
                if not json_data:
                    continue

                raw_is_finish_value = str(fields_dict.get("is_finish", "0"))
                is_finish = (raw_is_finish_value == "1")

                res = self._ta.validate_json(json_data)

                yield ChatStreamResponse(
                    seq=seq,
                    content=res,
                    is_finish=is_finish
                )
                seq+=1


            if last_stream_id:
                current_id = last_stream_id

    async def read_all_messages_from_stream(
        self,
        chat_id: int,
        conversation_id: str,
        offset: str | None = None
    ) -> list[ChatStreamResponse]:
        stream_key = f"{CHAT_MESSAGES_KEY}:{chat_id}:{conversation_id}"

        if offset is None:
            offset = "0-0"

        response: list[tuple[str, dict[str, Any]]] | None = await self.redis_client.xrange(
            stream_key,
            min=offset,
            max="+"
        )

        if not response:
            return []

        messages: list[ChatStreamResponse] = []

        for seq, (_stream_id, fields_dict) in enumerate(response, start=1):
            json_data = fields_dict.get("data", None)
            if not json_data:
                continue

            raw_is_finish_value = str(fields_dict.get("is_finish", "0"))
            is_finish = (raw_is_finish_value == "1")

            messages.append(
                ChatStreamResponse(
                    seq=seq,
                    is_finish=is_finish,
                    content=self._ta.validate_json(json_data)
                )
            )

        return messages


    async def add_stream_message(
        self,
        chat_id: int,
        conversation_id: str,
        contents: str,
        is_finish: bool
    ) -> str:
        stream_key = f"{CHAT_MESSAGES_KEY}:{chat_id}:{conversation_id}"

        stream_id = await self.redis_client.xadd(
            stream_key,
            {
                "data" : contents,
                "is_finish": "1" if is_finish else "0"
            }
        )
        return stream_id


    async def delete_stream_message(
        self,
        chat_id: int,
        conversation_id: str,
        wait_time: int
    ) -> None:
        stream_key = f"{CHAT_MESSAGES_KEY}:{chat_id}:{conversation_id}"

        await asyncio.sleep(wait_time)
        try:
            await self.redis_client.delete(stream_key)
        except Exception:
            raise


async def get_redis_stream_service(
    redis_client: RedisManager = Depends(get_redis_client)
) -> RedisStreamService:
    return RedisStreamService(
        redis_client=redis_client
    )
