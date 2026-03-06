# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from base_repository import BaseRepository
from fastapi import FastAPI

from common.infra.grpc.grpc import ModelStreamClient
from common.infra.mysql.mysql import get_mysql
from common.infra.redis import RedisManager, init_redis
from config.base_repo_config import MysqlSessionProvider
from config.config import (
    env_config,
    local_storage_config,
    object_storage_config,
    redis_clutser_config,
    service_config,
)
from uploads.infra.local_storage import LocalStorage
from uploads.infra.ncp_storage import NCPStorage


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis_client: RedisManager | None = None
    try:
        redis_client = await init_redis(redis_clutser_config)

        # Baserepo session provider 주입
        BaseRepository.configure_session_provider(MysqlSessionProvider())

        if env_config.STORAGE == "NCP":
            app.state.object_storage = NCPStorage(object_storage_config)
        elif env_config.STORAGE == "LOCAL":
            app.state.object_storage = LocalStorage(local_storage_config)

        app.state.model_stub = ModelStreamClient(service_config.MODEL_SERVER_GRPC_URL)

        yield

    finally:
        await app.state.model_stub.close()
        app.state.object_storage.close()

        mysql = get_mysql()
        await mysql.close()

        if redis_client:
            await redis_client.close()

