# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from assistant_adapter.database._in_assistant_storage import assistant_storage
from assistant_adapter.presentation.grpc_router import AssistantGrpcRouter
from assistant_adapter.database.assistant_repository import AssistantRepository
from assistant_adapter.service.assistant_service import AssistantService
from assistant_adapter.usecase.assistant_usecase import AssistantUseCase


def get_assistant_repository() -> AssistantRepository:
    return AssistantRepository(registry=assistant_storage)


def get_assistant_service() -> AssistantService:
    return AssistantService(repository=get_assistant_repository())


def get_assistant_usecase() -> AssistantUseCase:
    return AssistantUseCase(service=get_assistant_service())


def get_assistant_handler() -> AssistantGrpcRouter:
    return AssistantGrpcRouter(usecase=get_assistant_usecase())
