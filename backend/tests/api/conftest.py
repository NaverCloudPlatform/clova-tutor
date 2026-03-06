# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# DB 의존성입니다.
from collections.abc import AsyncGenerator, Iterator
from typing import cast

import pytest
import pytest_asyncio

from fakeredis import FakeAsyncRedis, FakeServer
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import RedisCluster
from sqlalchemy.ext.asyncio import AsyncSession

from common.infra.mysql.mysql import Mysql
from common.infra.redis import RedisManager, get_redis_client


@pytest_asyncio.fixture(scope="function")
async def db_session(app: FastAPI, mocked_mysql: Mysql) -> AsyncGenerator[AsyncSession, None]:
    """
    1) 실제 커넥션을 잡고
    2) AsyncSession 을 생성 → 트랜잭션 → SAVEPOINT
    3) yield 한 뒤 rollback & close
    """
    async with app.router.lifespan_context(app):
        conn = await mocked_mysql.engine.connect()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        tx = await session.begin()
        await session.begin_nested()
        try:
            yield session
        finally:
            await tx.rollback()
            await session.close()
            await conn.close()


@pytest_asyncio.fixture(autouse=True)
async def bind_test_session(mocked_mysql: Mysql, db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """
    테스트 환경에서는 Mysql._current_session 을
    테스트용 db_session 으로 강제로 바인딩한다.
    """
    token = mocked_mysql._current_session.set(db_session)
    try:
        yield
    finally:
        mocked_mysql._current_session.reset(token)

@pytest.fixture(autouse=True)
def override_get_redis_client(app: FastAPI) -> Iterator[None]:
    server = FakeServer()
    fake_low = FakeAsyncRedis(server=server, decode_responses=True)

    # 프로덕션 AsyncRedisClient를 그대로 쓰되, 내부 client만 fakeredis로 교체
    client = RedisManager(client=cast(RedisCluster, fake_low), default_ttl=3600)

    async def _override() -> RedisManager:
        return client

    app.dependency_overrides[get_redis_client] = _override
    app.state.redis = client  # 여기서 await 쓰지 말 것
    yield
    app.dependency_overrides.pop(get_redis_client, None)


@pytest.fixture(autouse=True)
def inject_internal_api_key(async_client: AsyncClient) -> None:
    """
    internal API 호출 시 필요한 X-API-Key 헤더 자동 주입.

    verify_internal_api_key(x_api_key: str | None = Header(None))
    와 동일한 키를 ENV 기반 config에서 읽어와 설정한다.
    """
    from config.config import internal_api_key
    async_client.headers.update(
        {
            "X-API-Key": internal_api_key.INTERNAL_API_KEY,
        }
    )
