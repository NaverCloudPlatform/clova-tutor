# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
import grpc

from assistant_adapter.usecase.assistant_usecase import AssistantUseCase
from grpc_stubs import modelchat_pb2_grpc

from common.logger import logger
from grpc_stubs.modelchat_pb2 import CreateChatTitleRequest


class AssistantGrpcRouter(modelchat_pb2_grpc.ModelServiceServicer):
    def __init__(self, usecase: AssistantUseCase):
        self.usecase = usecase

    async def GenerateResponse(self, request, context):
        try:
            async for chunk in self.usecase.model_stream(request):
                yield chunk
        except asyncio.CancelledError:
            # 클라이언트에서 취소한 경우
            raise
        except Exception as e:
            logger.exception("GenerateResponse failed: %s", e)
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GenerateChatTitle(self, request: CreateChatTitleRequest, context):
        try:
            return await self.usecase.create_chat_title(request)
        except Exception as e:
            logger.error("GenerateChatTitle failed: %s", e, exc_info=True)
            context.abort(grpc.StatusCode.INTERNAL, f"Internal server error: {e}")
