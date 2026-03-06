# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
import os
from typing import ClassVar, Optional

from redis import Redis
from redis.cluster import RedisCluster as SyncRedisCluster

from config.config import RedisClusterConfig


class RedisManager:
    _instance: ClassVar[Optional["RedisManager"]] = None
    _pid: ClassVar[int | None] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(
        self,
        sync_client: SyncRedisCluster,
        default_ttl: int,
    ) -> None:
        self._sync_client = sync_client
        self.default_ttl = default_ttl

        if hasattr(os, "register_at_fork"):
            os.register_at_fork(after_in_child=self._after_fork)

    @classmethod
    async def ensure_initialized(
        cls, config: RedisClusterConfig
    ) -> "RedisManager":
        pid = os.getpid()
        if cls._instance is not None and cls._pid == pid:
            # 빠른 경로: 이미 초기화된 경우
            return cls._instance

        async with cls._lock:
            if cls._instance is not None and cls._pid == pid:
                # 더블 체크: Lock 획득 후 다시 확인
                return cls._instance

            # 동기 및 비동기 클라이언트 모두 생성
            sync_client = await cls._create_client(config)

            # 인스턴스 생성 및 저장
            cls._instance = cls(
                sync_client=sync_client,
                default_ttl=3600,
            )
            cls._pid = pid
            return cls._instance

    def _after_fork(self) -> None:
        """fork 후 자식 프로세스에서 실행되어 싱글톤 인스턴스를 초기화합니다."""
        type(self)._instance = None
        type(self)._pid = None

    @classmethod
    def get_instance(cls) -> "RedisManager":
        """
        싱글톤 객체 받을 때 사용
        """
        if cls._instance is None or cls._pid != os.getpid():
            raise RuntimeError(
                "Redis not initialized. Call RedisManager.ensure_initialized() first."
            )
        return cls._instance

    # ---------- 클라이언트 생성 ----------

    #     return sync_client
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

    async def close(self) -> None:
        if self._sync_client is not None:
            self._sync_client.close()


async def init_redis(config: RedisClusterConfig) -> RedisManager:
    return await RedisManager.ensure_initialized(config)


def get_sync_redis_client() -> SyncRedisCluster:
    _instance = RedisManager.get_instance()
    return _instance._sync_client
