# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


from collections.abc import AsyncGenerator

import grpc

from fastapi import Request

from common.infra.grpc.grpc_stubs import modelchat_pb2_grpc
from common.infra.grpc.grpc_stubs.modelchat_pb2 import (
    CreateChatTitleRequest,
    CreateChatTitleResponse,
    ModelRequest,
    ModelResponse,
)
from common.infra.grpc.resilient_interceptor import ResilientInterceptor
from common.utils.circuit_breaker import CircuitBreaker


class ModelStreamClient:
    def __init__(self, grpc_server_url: str) -> None:
        self.interceptor = ResilientInterceptor(circuit_breaker=CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        ))

        self.grpc_server_url = grpc_server_url
        self._connect()

    def _connect(self) -> None:
        self.channel = grpc.aio.insecure_channel(
            self.grpc_server_url,
            interceptors=[self.interceptor]
        )
        self.stub = modelchat_pb2_grpc.ModelServiceStub(self.channel) # type: ignore

    async def _reconnect(self) -> None:
        await self.close()
        self._connect()


    async def create_chat_title(self, request: CreateChatTitleRequest) -> CreateChatTitleResponse:
        return await self.stub.GenerateChatTitle(request) # type: ignore


    async def stream(self, request: ModelRequest) -> AsyncGenerator[ModelResponse, None]:
        async for chunk in self.stub.GenerateResponse(request):
            yield chunk


    async def close(self) -> None:
        await self.channel.close()


async def get_model_stub(request: Request) -> ModelStreamClient:
    return request.app.state.model_stub # type: ignore
