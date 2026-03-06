# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import os

from collections.abc import AsyncGenerator, Generator
from unittest.mock import patch

import pytest
import pytest_asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from common.infra.mysql.mysql import Mysql
from common.infra.redis import RedisManager
from config.config import DBConfig, RedisClusterConfig

DB_CONFIG_PATH = "config.config.db_config"
TEST_DB_NAME = "local"


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI, None, None]:
    patcher = patch(DB_CONFIG_PATH, new=DBConfig(MYSQL_DB=TEST_DB_NAME))
    patcher.start()

    from main import app as _app

    with TestClient(_app):
        yield _app

    patcher.stop()


@pytest_asyncio.fixture(scope="session")
async def redis_client() -> AsyncGenerator[RedisManager, None]:
    dns = os.getenv("RC_SEED_URL", "")
    path = os.getenv("RC_PASSWORD", "")
    ttl = int(os.getenv("REDIS_TTL", 3600))

    client = await RedisManager.ensure_initialized(
        RedisClusterConfig(
            RC_SEED_URL=dns,
            RC_PASSWORD=path,
            RC_TTL=ttl,
        )
    )
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="function")
async def mocked_mysql() -> AsyncGenerator[Mysql, None]:
    test_config = DBConfig(MYSQL_DB=TEST_DB_NAME)
    test_mysql = Mysql(test_config)

    # 싱글톤 교체
    Mysql._instance = test_mysql
    Mysql._pid = os.getpid()

    yield test_mysql

    # 세션 끝나면 연결 해제 + 원상 복구
    await test_mysql.close()
    Mysql._instance = None
    Mysql._pid = None



# 비동기 Client 입니다.
@pytest_asyncio.fixture(scope="function")
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as c:
            yield c

