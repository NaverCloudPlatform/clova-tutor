# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from __future__ import annotations

import os

from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, Concatenate, ParamSpec, TypeVar, overload

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.infra.mysql.resilient_async_session import ResilientAsyncSession
from config.config import DBConfig, db_config, env_config


class Mysql:
    _instance: Mysql | None = None
    _pid: int | None = None
    _current_session: ContextVar[AsyncSession | None] = ContextVar("mysql_current_session", default=None)


    def __init__(self, config: DBConfig) ->  None:
        self.engine = create_async_engine(
            URL.create(
                "mysql+aiomysql",
                username=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                host=config.MYSQL_HOST,
                port=int(config.MYSQL_PORT),
                database=config.MYSQL_DB
            ),
            echo=False,
            pool_pre_ping=True,
            pool_recycle=28000,
        )

        self.Session = async_sessionmaker(
            bind=self.engine,
            class_=ResilientAsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        if hasattr(os, "register_at_fork"):
            os.register_at_fork(after_in_child=self._after_fork)

    @classmethod
    def get(cls, config: DBConfig | None = None) -> Mysql:
        pid = os.getpid()
        if cls._instance is None or cls._pid != pid:
            if config is None:
                config = db_config
            cls._instance = cls(config)
            cls._pid = pid
        return cls._instance

    def _after_fork(self) -> None:
        type(self)._instance = None
        type(self)._pid = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        s = self.Session()
        try:
            yield s
        finally:
            await s.close()

    @asynccontextmanager
    async def contextual_session(self) -> AsyncGenerator[AsyncSession, None]:
        existing = self._current_session.get()
        if existing is not None:
            yield existing
            return

        async with self.transactional_session() as s:
            yield s

    @asynccontextmanager
    async def transactional_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session() as s:
            token = self._current_session.set(s)
            try:
                yield s
                await s.commit()
            except Exception:
                try:
                    await s.rollback()
                finally:
                    self._current_session.reset(token)
                raise
            else:
                self._current_session.reset(token)

    @classmethod
    def current_session(cls) -> AsyncSession:
        s = cls._current_session.get()
        if s is None:
            raise RuntimeError(
                "DB 세션 컨텍스트 없음. 원인은 다음과같을겁니다 \n",
                "1. FastAPI의 미들웨어가 요청마다 contextual_session을 호출하는지 확인하세요"
                "2. FastAPI가 아닌 환경에서 실행시켰습니다. 아 경우 contextual_session 혹은 transactional_session을 사용해서 세션을 채워줘야합니다."
            )
        return s

    async def close(self) -> None:
        await self.engine.dispose()


def get_mysql() -> Mysql:
    return Mysql.get()

P = ParamSpec("P")
R = TypeVar("R")

@overload
def transactional(
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R]]:
    ...


@overload
def transactional(
    func: None = None,
    *,
    force_new: bool = ...,
) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
    ...


def transactional(
    func: Callable[P, Coroutine[Any, Any, R]] | None = None,
    *,
    force_new: bool = False,
) -> Callable[P, Coroutine[Any, Any, R]] | Callable[
    [Callable[P, Coroutine[Any, Any, R]]],
    Callable[P, Coroutine[Any, Any, R]],
]:
    """
    < 비즈니스 로직 전체를 하나의 트랜잭션으로 묶는다 >

    사용 방식:
        @transactional
        async def do_something(...):
            repo = SomeRepository()
            await repo.create(...)
            await repo.update(...)
            ## 함수 전체가 하나의 트랜잭션으로 취급됨
            ## 단 repo.create 등에서 명시적으로 commit을 하였으면 하나의 트랜잭션을 보장하지않는다.

    - force_new=True:
        바깥에 트랜잭션이 있어도 무조건 새 transactional_session()을 연다.
        (해당 블록에서는 독립 세션 사용, 종료 시 바깥 세션 컨텍스트 복원)

    동작 원리:
        1. 이미 트랜잭션이 진행중이면(예: 상위 함수가 @transactional)
           - 새로운 트랜잭션 생성하지 않음
           - 현재 컨텍스트의 세션 재사용
           - 커밋/롤백 책임도 상위 트랜잭션에 있음

        2. 트랜잭션이 없으면
           - mysql.transactional_session() 으로 새 트랜잭션 생성
           - 함수 실행 종료 시점에 commit
           - 예외 발생 시 rollback


    주의사항:
        - 데코레이터는 “세션 객체"를 함수 인자로 전달하지 않음.
        - Repo 내부에서 Mysql.current_session() 으로 동일 세션을 가져와 사용해야 함.
        - Celery, Scheduler 등 FastAPI 미들웨어가 없는 환경에서도 동일하게 작동함.
          (각 worker task 시작 부분에서 transactional 로 트랜잭션을 열면 됨)
    """

    def decorator(
        fn: Callable[P, Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            mysql = get_mysql()

            existing = mysql._current_session.get()

            # 1) 기본 모드: 기존 세션 재사용
            if existing is not None and not force_new:
                return await fn(*args, **kwargs)

            # 2) force_new 이거나, 세션이 없는 경우: 새 transactional_session
            async with mysql.transactional_session():
                return await fn(*args, **kwargs)

        return wrapper

    # @transactional
    if func is not None and callable(func):
        return decorator(func)

    # @transactional(force_new=True)
    return decorator


@overload
def transactional_with_session(
    func: Callable[Concatenate[AsyncSession, P], Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R]]:
    ...


@overload
def transactional_with_session(
    func: None = None,
    *,
    force_new: bool = ...,
) -> Callable[
    [Callable[Concatenate[AsyncSession, P], Coroutine[Any, Any, R]]],
    Callable[P, Coroutine[Any, Any, R]],
]:
    ...


def transactional_with_session(
    func: Callable[Concatenate[AsyncSession, P], Coroutine[Any, Any, R]] | None = None,
    *,
    force_new: bool = False,
) -> Callable[P, Coroutine[Any, Any, R]] | Callable[
    [Callable[Concatenate[AsyncSession, P], Coroutine[Any, Any, R]]],
    Callable[P, Coroutine[Any, Any, R]],
]:
    """
    첫 번째 인자로 AsyncSession을 주입하는 트랜잭션 데코레이터

    기본:
        - 이미 세션 있으면 그 세션을 첫 번째 인자로 주입
        - 없으면 transactional_session()으로 새 세션 생성

    force_new=True:
        - 바깥 세션이 있어도 무조건 새 transactional_session() 생성
    """

    def decorator(
        fn: Callable[Concatenate[AsyncSession, P], Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            mysql = get_mysql()
            existing = mysql._current_session.get()

            # 기본 모드: 기존 세션 재사용
            if existing is not None and not force_new:
                session = existing
                return await fn(session, *args, **kwargs)

            # force_new 이거나, 세션이 없는 경우: 새 transactional_session
            async with mysql.transactional_session() as session:
                return await fn(session, *args, **kwargs)

        return wrapper

    # @transactional_with_session
    if func is not None and callable(func):
        return decorator(func)

    # @transactional_with_session(force_new=True)
    return decorator
