# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, TypeVar, cast

import grpc

from common.utils.circuit_breaker import CircuitBreaker

# 제네릭 타입 정의
RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


class ResilientInterceptor(
    grpc.aio.UnaryUnaryClientInterceptor, # type: ignore
    grpc.aio.UnaryStreamClientInterceptor # type: ignore
):
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.cb = circuit_breaker


    async def _handle_call(
        self,
        continuation: Callable[[grpc.aio.ClientCallDetails, RequestT], Awaitable[grpc.aio.UnaryUnaryCall |grpc.aio.UnaryStreamCall]],
        client_call_details: grpc.aio.ClientCallDetails,
        request: RequestT,
        is_stream: bool = False
    ) -> Any:
        # 서킷 상태 확인 및 락 획득
        tester: bool = await self.cb.before_call()

        try:
            # 실제 RPC 호출 실행
            response = await continuation(client_call_details, request)

            if is_stream:
                # 스트림일 경우 response는 AsyncIterable 성격을 가짐
                return self._consume_stream(cast(grpc.aio.UnaryStreamCall, response), tester)

            # 단발성(Unary)일 경우 결과 반환 후 성공 처리
            self.cb.on_success(tester)
            return response

        except Exception as exc:
            self._handle_exception(exc, tester)
            raise

    async def _consume_stream(
        self,
        stream: grpc.aio.UnaryStreamCall,
        tester: bool
    ) -> AsyncGenerator[Any, None]:
        """스트림 데이터를 소비하며 에러를 감시합니다."""
        try:
            async for chunk in stream:
                yield chunk
            self.cb.on_success(tester)
        except Exception as exc:
            self._handle_exception(exc, tester)
            raise

    def _handle_exception(self, exc: Exception, tester: bool) -> None:
        # 사용자가 정의한 에러 핸들링 로직
        if isinstance(exc, grpc.aio.AioRpcError | ConnectionError):
            self.cb.on_failure(tester)
        else:
            self.cb.release_half_open_lock(tester)

    # ---------- Interceptor 필수 구현 메서드 ----------

    async def intercept_unary_unary(
        self,
        continuation: Callable[[grpc.aio.ClientCallDetails, RequestT], Awaitable[grpc.aio.UnaryUnaryCall]],
        client_call_details: grpc.aio.ClientCallDetails,
        request: RequestT
    ) -> grpc.aio.UnaryUnaryCall:
        return await self._handle_call(continuation, client_call_details, request, is_stream=False)

    async def intercept_unary_stream(
        self,
        continuation: Callable[[grpc.aio.ClientCallDetails, RequestT], Awaitable[grpc.aio.UnaryStreamCall]],
        client_call_details: grpc.aio.ClientCallDetails,
        request: RequestT
    ) -> grpc.aio.UnaryStreamCall |  AsyncGenerator[Any, None]:
        # 실제로는 _consume_stream이 AsyncGenerator를 반환함
        return await self._handle_call(continuation, client_call_details, request, is_stream=True)
