# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import logging

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends

from chats.domain.chat_message.chat_message import ChatStreamStatus
from chats.service.i_stream_lock_service import IStreamLockService, StreamStatusResponse
from common.infra.redis import RedisManager, get_redis_client
from common.utils.logger import ServiceLogType, register_internal_service_log

CHAT_STREAM_STATE_KEY = "chat:state"
DEFAULT_TTL = 60

class RedisStreamLockService(IStreamLockService):
    def __init__(
        self,
        redis_client: RedisManager
    ):
        self.redis_client = redis_client

    async def check_status(
        self,
        chat_id: int,
        request_id: str | None
    ) -> StreamStatusResponse:
        redis_key = f"{CHAT_STREAM_STATE_KEY}:{chat_id}"

        active_id = await self.redis_client.get(redis_key)

        status = ChatStreamStatus.COMPLETE
        if active_id:
            if request_id is None:
                status = ChatStreamStatus.IS_STREAMING

            elif request_id == active_id:
                status = ChatStreamStatus.IS_STREAMING

        return StreamStatusResponse(
            status=status,
            stream_id=active_id
        )


    async def release_lock(
        self,
        chat_id: int,
    ) -> None:
        redis_key = f"{CHAT_STREAM_STATE_KEY}:{chat_id}"
        try:
            await self.redis_client.delete(redis_key)
        except Exception as e:
            register_internal_service_log(
                f"Redis Lock DELETE Failed : {e}",
                log_type=ServiceLogType.SYSTEM,
                level=logging.ERROR
            )

    @asynccontextmanager
    async def acquire_lock(
        self,
        chat_id: int,
        request_id: str,
        ttl: int | None = None,
    ) -> AsyncIterator[bool]:
        acquired = False
        redis_key = f"{CHAT_STREAM_STATE_KEY}:{chat_id}"

        if ttl is None:
            ttl = DEFAULT_TTL

        try:
            result = await self.redis_client.set(
                redis_key,
                str(request_id),
                ttl=ttl,
                nx=True
            )
            acquired = result
        except Exception as e:
            register_internal_service_log(
                f"Redis Lock SET Failed : {e}",
                log_type=ServiceLogType.SYSTEM,
                level=logging.ERROR
            )
            # Fail-Open 정책 (Redis)
            acquired = True

        yield acquired

        if acquired:
            cur_status = await self.check_status(chat_id=chat_id, request_id=request_id)
            if cur_status.stream_id == request_id:
                await self.release_lock(chat_id)


async def get_redis_lock_service(
    redis_client: RedisManager = Depends(get_redis_client)
) -> RedisStreamLockService:
    return RedisStreamLockService(
        redis_client=redis_client
    )
