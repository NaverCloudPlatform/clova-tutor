# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Annotated, Any

from sqlalchemy.engine import Result
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.exc import TimeoutError as SATimeoutError
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Doc

from common.utils.circuit_breaker import RESILIENCE_RETRIES, CircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0,
)

def _is_transient_db_error(exc: BaseException) -> bool:
    """일시적인 DB 오류로 간주할 예외인지 여부를 반환한다.

    다음과 같은 경우를 일시적인 오류로 취급한다.

    * DBAPIError 이면서 connection_invalidated 플래그가 True인 경우
    * OperationalError (네트워크 및 연결 계열 오류)
    * SQLAlchemy TimeoutError (풀 커넥션 획득 실패, 쿼리 타임아웃 등)
    """
    if isinstance(exc, DBAPIError) and getattr(exc, "connection_invalidated", False):
        return True
    if isinstance(exc, OperationalError | SATimeoutError):
        return True
    return False


class ResilientAsyncSession(AsyncSession):
    """서킷 브레이커와 재시도 로직이 적용된 AsyncSession 구현.

    이 세션의 execute 메서드는 모든 쿼리 실행 전에 CircuitBreaker를 통해
    상태를 확인하고, 일시적인 DB 오류에 대해서는 제한된 횟수만큼 재시도를 수행한다.
    """

    async def _raw_execute(
        self,
        statement: Any,
        params: Any | None = None,
        *,
        execution_options: Any | None = None,
        bind_arguments: Any | None = None,
        **kw: Any,
    ) -> Result[Any]:
        raw = await super().execute(
            statement=statement,
            params=params,
            execution_options=execution_options or {},
            bind_arguments=bind_arguments,
            **kw,
        )
        return raw


    async def execute(
        self,
        statement: Annotated[
            Any,
            Doc("실행할 SQLAlchemy 문장(Executable) 또는 ORM 쿼리 객체"),
        ],
        params: Annotated[
            Any | None,
            Doc("바인딩 파라미터(매핑 또는 시퀀스)"),
        ] = None,
        *,
        execution_options: Annotated[
            Any | None,
            Doc("SQLAlchemy execution_options 딕셔너리"),
        ] = None,
        bind_arguments: Annotated[
            Any | None,
            Doc("바인딩에 사용할 추가 인수 딕셔너리"),
        ] = None,
        **kw: Annotated[
            Any,
            Doc("그 외 SQLAlchemy execute 에 전달할 추가 키워드 인수"),
        ],
    ) -> Result[Any]:
        """서킷 브레이커 보호가 적용된 쿼리 실행 메서드.

        동작
        ----
        1. CircuitBreaker.before_call()을 통해 서킷 상태를 검사한다.
        2. 허용된 경우 AsyncSession.execute()를 호출한다.
        3. 일시적인 DB 오류로 판단되면 RESILIENCE_RETRIES 설정에 따라 재시도한다.
        4. 재시도 후에도 실패하면 CircuitBreaker.on_failure()를 호출하고 예외를 전파한다.
        5. 도메인 예외 등 비 DB 오류는 CircuitBreaker.on_non_db_error()를 호출한다.
        """
        async def _operation() -> Result[Any]:
            return await self._raw_execute(
                statement=statement,
                params=params,
                execution_options=execution_options,
                bind_arguments=bind_arguments,
                **kw,
            )

        result = await circuit_breaker.call(
            operation=_operation,
            retries=RESILIENCE_RETRIES,
            handled_exceptions=(
                DBAPIError,
                OperationalError,
                SATimeoutError,
            ),
            is_transient=_is_transient_db_error,
        )

        return result
