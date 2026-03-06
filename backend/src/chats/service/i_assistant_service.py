# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from chats.domain.assistant.assistant_request import AssistantRequest
from chats.domain.assistant.assistant_response import AssistantResponse


class IAssistantService(ABC):
    @abstractmethod
    def get_model_stream_response(self, request: AssistantRequest) -> AsyncIterator[AssistantResponse]:
        ...


    @abstractmethod
    async def create_chat_title(self, request: str) -> str:
        ...

