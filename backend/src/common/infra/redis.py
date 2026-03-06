# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
import os

from collections.abc import Awaitable, Callable
from typing import Any, ClassVar, Optional, cast

from redis.asyncio import Redis
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    RedisClusterException,
    TimeoutError,
)
from redis.typing import EncodableT, FieldT, KeyT, StreamIdT

from common.utils.circuit_breaker import CircuitBreaker
from config.config import RedisClusterConfig

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0,
)

redis_circuit_error = (TimeoutError, ConnectionError,BusyLoadingError, RedisClusterException )

def is_redis_transient(exc: BaseException) -> bool:
    # 명시적으로 "잠깐 후 재시도" 의미를 가진 예외들
    if isinstance(
        exc,
        redis_circuit_error,
    ):
        return True

    # RedisError지만 위에 해당 안 되면 대부분 논리/명령 오류
    return False

class RedisManager:
    """
    - 프로세스 단위 싱글톤 (prefork 환경 안전)
    - 비동기 초기화 1회 보장(더블 체크 + asyncio.Lock)
    - 요청 DI 없이 전역 접근(get_redis) 제공
    """

    _instance: ClassVar[Optional["RedisManager"]] = None
    _pid: ClassVar[int | None ] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()


    def __init__(self, client: Redis, default_ttl: int) -> None:
        self.client = client
        self.default_ttl = default_ttl
        if hasattr(os, "register_at_fork"):
            os.register_at_fork(after_in_child=self._after_fork)

    # 싱글톤
    @classmethod
    async def ensure_initialized(cls, config: RedisClusterConfig) -> "RedisManager":
        pid = os.getpid()
        if cls._instance is not None and cls._pid == pid:
            return cls._instance

        async with cls._lock:
            if cls._instance is not None and cls._pid == pid:
                return cls._instance

            client = await cls._create_client(config)
            cls._instance = cls(client=client, default_ttl=int(config.RC_TTL))
            cls._pid = pid
            return cls._instance


    @classmethod
    def get_instance(cls) -> "RedisManager":
        """
        싱글톤 객체 받을 때 사용
        """
        if cls._instance is None or cls._pid != os.getpid():
            raise RuntimeError("Redis not initialized. Call AsyncRedisClient.ensure_initialized() first.")
        return cls._instance


    def _after_fork(self) -> None:
        type(self)._instance = None
        type(self)._pid = None


    # ---------- 클라이언트 생성 ----------
    @classmethod
    async def _create_client(cls, config: RedisClusterConfig) -> Redis:
        parts = config.RC_SEED_URL.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 6379
        
        # Standalone Redis 클라이언트 생성
        client = Redis(
            host=host,
            port=int(port),
            password=config.RC_PASSWORD,
            decode_responses=True,
            socket_timeout=5.0
        )
        return client


    async def _guard(self, operation: Callable[[], Awaitable[Any]]) -> Any:
        return await circuit_breaker.call(
            operation=operation,
            retries=5,
            handled_exceptions=redis_circuit_error,
            is_transient=is_redis_transient
        )

    # Redis Set 관련 메소드
    async def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        async def _op() -> Any:
            _ttl = ttl if ttl is not None else self.default_ttl
            return await self.client.set(key, value, ex=_ttl, nx=nx, xx=xx)

        return cast(bool, await self._guard(_op))


    async def get(self, key: str) -> str | None:
        async def _op() -> Any:
            result = await self.client.get(key)
            if result is None:
                return None
            return str(result)

        return cast(str | None, await self._guard(_op))


    async def delete(self, key: str) -> None:
        async def _op() -> Any:
            await self.client.delete(key)

        await self._guard(_op)


    async def expire(self, key: str, ttl: int | None = None) -> Any:
        async def _op() -> Any:
            _ttl = ttl if ttl is not None else self.default_ttl
            return await self.client.expire(key, _ttl)

        return await self._guard(_op)


    # Redis Streams 관련 메소드
    async def xadd(
        self,
        key: KeyT,
        fields: dict[FieldT, EncodableT],
        stream_id: StreamIdT = "*",
    ) -> str:
        async def _op() -> Any:
            return await self.client.xadd(key, fields, id=stream_id)

        return cast(str, await self._guard(_op))


    async def xrange(
        self,
        key: KeyT,
        min: StreamIdT | None = None,
        max: StreamIdT | None = None,
        count: int | None = None,
    ) -> Any:
        async def _op() -> Any:
            kwargs: dict[str, Any] = {}
            if min is not None:
                kwargs["min"] = min
            if max is not None:
                kwargs["max"] = max
            if count is not None:
                kwargs["count"] = count

            return await self.client.xrange(key, **kwargs)

        return await self._guard(_op)


    async def xread(
        self,
        streams: dict[KeyT, StreamIdT],
        count: int | None = None,
        block: int | None = None,
    ) -> Any:
        async def _op() -> Any:
            return await self.client.xread(streams, count=count, block=block)

        return await self._guard(_op)


    async def xdel(self, stream_key: KeyT, *ids: StreamIdT) -> int:
        async def _op() -> Any:
            return await self.client.xdel(stream_key, *ids)

        return cast(int, await self._guard(_op))


    async def xtrim(
        self,
        key: KeyT,
        *,
        max_len: int | None = None,
        approximate: bool = True,
        min_id: StreamIdT | None = None,
        limit: int | None = None,
    ) -> int:
        async def _op() -> Any:
            return await self.client.xtrim(
                name=key,
                maxlen=max_len,
                approximate=approximate,
                minid=min_id,
                limit=limit,
            )

        return cast(int, await self._guard(_op))


    async def close(self) -> None:
        if self.client is not None:
            await self.client.aclose()


async def init_redis(config: RedisClusterConfig) -> RedisManager:
    return await RedisManager.ensure_initialized(config)


def get_redis_client() -> RedisManager:
    return RedisManager.get_instance()
