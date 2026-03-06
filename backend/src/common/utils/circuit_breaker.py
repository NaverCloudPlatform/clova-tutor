# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from __future__ import annotations

import asyncio
import time

from collections.abc import Awaitable, Callable
from enum import IntEnum
from typing import Annotated, TypeVar

from typing_extensions import Doc

__all__ = [
    "RESILIENCE_RETRIES",
    "CircuitOpenError",
    "CircuitBreaker",
]


RESILIENCE_RETRIES: Annotated[
    int,
    Doc("일시 오류 발생 시 재시도 횟수 (1이면 총 2회 시도)"),
] = 1


class CircuitState(IntEnum):
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2


class CircuitOpenError(RuntimeError):
    """서킷이 OPEN 또는 HALF_OPEN 상태여서 요청이 허용되지 않을 때 발생하는 예외."""

T = TypeVar("T")
AsyncOperation = Callable[[], Awaitable[T]]
ExceptionPredicate = Callable[[BaseException], bool]


class CircuitBreaker:
    """서킷 브레이커.

    상태
    ----
    CLOSED
        정상 상태로, 모든 호출을 허용한다. 실패 횟수만 누적된다.
    OPEN
        설정된 실패 임계값을 초과한 상태로, 지정된 시간 동안 모든 호출을 거부한다.
    HALF_OPEN
        회복 여부를 확인하기 위해 정확히 한 개의 테스트 호출만 허용한다.
    """

    def __init__(
        self,
        *,
        failure_threshold: Annotated[
            int,
            Doc("OPEN 상태로 전환하기 위한 연속 실패 횟수 임계값"),
        ] = 5,
        recovery_timeout: Annotated[
            float,
            Doc("OPEN 상태에서 HALF_OPEN 상태로 전환되기까지 대기할 시간(초)"),
        ] = 30.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self._state: Annotated[
            CircuitState,
            Doc("현재 서킷 상태: 'CLOSED', 'OPEN', 'HALF_OPEN' 중 하나"),
        ] = CircuitState.CLOSED
        self._failure_count: Annotated[
            int,
            Doc("연속적으로 발생한 실패 횟수"),
        ] = 0
        self._last_failure_time: Annotated[
            float,
            Doc("마지막 실패가 발생한 시각 (time.time() 기준 초 단위)"),
        ] = 0.0

        # HALF_OPEN 상태에서 테스트 호출 1개만 허용하기 위한 락
        self._half_open_lock = asyncio.Lock()

    def _update_state_for_timeout(self) -> None:
        """OPEN 상태에서 recovery_timeout 경과 여부에 따라 HALF_OPEN으로 전환한다."""
        if self._state != CircuitState.OPEN:
            return

        if time.time() - self._last_failure_time >= self.recovery_timeout:
            self._state = CircuitState.HALF_OPEN


    async def call(
        self,
        operation: Annotated[
            AsyncOperation[T],
            Doc("실제로 실행할 비동기 작업"),
        ],
        *,
        retries: Annotated[
            int,
            Doc("일시 오류에 대해 재시도할 횟수"),
        ] = 0,
        handled_exceptions: Annotated[
            tuple[type[BaseException], ...],
            Doc("서킷에 영향을 주는 인프라 계열 예외 타입 튜플"),
        ],
        is_transient: Annotated[
            ExceptionPredicate,
            Doc("주어진 예외가 재시도 대상(일시 오류)인지 판별하는 함수"),
        ],
    ) -> T:
        """
        서킷 브레이커 보호 하에 비동기 작업을 실행합니다
        """
        tester = await self.before_call()
        last_exc: BaseException | None = None

        for attempt in range(retries + 1):
            try:
                result = await operation()
                self.on_success(tester)
                return result

            except handled_exceptions as exc:
                last_exc = exc

                if attempt < retries and is_transient(exc):
                    # 재시도 대상인 인프라 오류
                    continue

                # 재시도 불가 혹은 횟수 초과 -> 서킷에 실패 반영
                self.on_failure(tester)
                raise

            except Exception as exc:
                # 정의하지않은 예외: 서킷 상태는 건드리지 않고 HALF_OPEN 락만 정리
                last_exc = exc
                self.release_half_open_lock(tester)
                raise

        assert last_exc is not None
        raise last_exc


    async def before_call(self) -> bool:
        """호출 전 서킷 상태를 확인한다.

        반환값
        ------
        bool
            True  : HALF_OPEN 상태에서 허용된 단일 테스트 호출인 경우
            False : 그 외 일반 호출인 경우

        예외
        ----
        CircuitOpenError
            서킷이 OPEN 상태이거나, HALF_OPEN 상태에서 이미 다른 테스트 호출이 진행 중인 경우
        """
        self._update_state_for_timeout()

        if self._state == CircuitState.OPEN:
            raise CircuitOpenError("DB circuit is OPEN (too many failures)")

        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_lock.locked():
                raise CircuitOpenError(
                    "DB circuit is HALF_OPEN and a test call is already running"
                )
            await self._half_open_lock.acquire()
            return True

        return False


    def on_success(self, tester: bool) -> None:
        """성공적인 호출을 기록한다.

        성공 시에는 실패 횟수를 초기화하고 상태를 CLOSED로 되돌린다.
        HALF_OPEN 상태에서의 테스트 호출이라면 내부 락을 해제한다.
        """
        self._failure_count = 0
        self._state = CircuitState.CLOSED

        if tester and self._half_open_lock.locked():
            self._half_open_lock.release()


    def on_failure(self, tester: bool) -> None:
        """서킷 상태에 영향을 주는 실패를 기록한다.

        DB 연결 오류와 같이 회복 가능한 인프라 실패를 전달할 때 사용한다.
        실패 횟수가 임계값 이상이면 상태를 OPEN으로 전환한다.
        HALF_OPEN 상태에서의 테스트 호출이라면 내부 락을 해제한다.
        """
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN

        if tester and self._half_open_lock.locked():
            self._half_open_lock.release()


    def release_half_open_lock(self, tester: bool) -> None:
        """
        애플리케이션 도메인 예외처럼 DB 상태와 무관한 실패에 사용한다.
        HALF_OPEN 상태에서의 테스트 호출이라면 내부 락만 정리한다.
        """
        if tester and self._half_open_lock.locked():
            self._half_open_lock.release()


    @property
    def state(self) -> Annotated[
        CircuitState,
        Doc("CircuitState ('CLOSED = 0', 'OPEN = 1', 'HALF_OPEN = 2')"),
    ]:
        """현재 서킷 상태를 반환한다."""
        return self._state
