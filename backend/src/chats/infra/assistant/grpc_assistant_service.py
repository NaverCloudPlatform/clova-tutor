# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import logging

from collections.abc import AsyncIterator

from fastapi import Depends

from chats.domain.assistant.assistant_request import AssistantRequest
from chats.domain.assistant.assistant_response import AssistantResponse
from chats.infra.assistant.grpc_assistant_mapper import GrpcAssistantMapper
from chats.service.i_assistant_service import IAssistantService
from common.infra.grpc.grpc import ModelStreamClient, get_model_stub
from common.infra.grpc.grpc_stubs.modelchat_pb2 import CreateChatTitleRequest
from common.utils.logger import register_internal_service_log


class GrpcAssistantService(IAssistantService):
    def __init__(
        self,
        grpc_stub: ModelStreamClient
    ):
        self.grpc_stub = grpc_stub

    async def get_model_stream_response(self, request: AssistantRequest) -> AsyncIterator[AssistantResponse]:
        model_req = GrpcAssistantMapper.to_grpc_model(request)
        try:
            model_stream_generator = self.grpc_stub.stream(model_req)

            async for grpc_chunk in model_stream_generator:
                assistant_response_chunk = GrpcAssistantMapper.to_assistant_response(grpc_chunk)
                yield assistant_response_chunk
        except Exception as e:
            register_internal_service_log(f"grpc Error : {e}", level=logging.ERROR)
            raise

    async def create_chat_title(self, request: str) -> str:
        model_req = CreateChatTitleRequest(user_input=request)

        response = await self.grpc_stub.create_chat_title(model_req)

        return response.title



async def get_grpc_assistant_service(
    grpc_stub: ModelStreamClient = Depends(get_model_stub),
) -> GrpcAssistantService:
    return GrpcAssistantService(
        grpc_stub=grpc_stub
    )
