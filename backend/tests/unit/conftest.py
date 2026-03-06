# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio

from collections.abc import AsyncGenerator

import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from common.infra.mysql.mysql import Mysql


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_session(mocked_mysql: Mysql) -> AsyncGenerator[AsyncSession, None]:
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
def mock_asyncio_create_task(monkeypatch):
    async def _run(coro):
        await coro
    monkeypatch.setattr(asyncio, "create_task", _run)
