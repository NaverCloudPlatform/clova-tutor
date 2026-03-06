# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from typing import AsyncGenerator

from assistant_adapter.domain.assistant_state import AssistantState, ResponseStyle
from assistant_adapter.service.assistant_service import (
    AssistantService,
)
from grpc_stubs.modelchat_pb2 import (
    CreateChatTitleRequest,
    CreateChatTitleResponse,
    ModelRequest,
    ModelResponse,
    PresentationOption,
    RecommendationInfo,
)


class AssistantUseCase:
    def __init__(self, service: AssistantService):
        self.service = service

    async def create_chat_title(
        self, request: CreateChatTitleRequest
    ) -> CreateChatTitleResponse:

        title = await self.service.create_chat_title(request.user_input)
        return CreateChatTitleResponse(title=title)

    async def model_stream(
        self, request: ModelRequest
    ) -> AsyncGenerator[ModelResponse, None]:
        req_id = request.request_id
        created = int(datetime.now().timestamp())
        chat_id = request.chat_id

        assistant = await self.service.get_or_create_assistant(
            user_id=request.user_id,
            chat_id=chat_id,
            name=request.user_name,
            grade=request.grade,
            subject=request.subject,
        )

        async for state in self.service.stream_response(
            assistant,
            user_query=request.user_query,
            images=list(request.image_url),
            vector_problem_id=request.vector_problem_id,
        ):
            yield self._to_grpc_message(req_id, created, state)

    @staticmethod
    def _to_grpc_message(req_id, created, state: AssistantState):
        # 1) 상위 메시지 작성
        msg = ModelResponse(
            id=req_id,
            created=created,
            finish=state.is_final,
            model_response=getattr(state, "model_response", ""),
        )
        if state.subject:
            msg.subject = state.subject
        if state.reference_image_document:
            msg.reference_image_document.extend(state.reference_image_document)

        # 2) RecommendationInfo 메시지 추가
        rec = RecommendationInfo(
            recommend_tool=state.recommend_tool,
            recommended_problem_id=state.recommended_problem_id,
        )

        msg.recommendation.CopyFrom(rec)

        # 3) PresentationOption 메시지 추가
        if len(state.response_styles) > 0:
            # FYI: TABLE_FETCH 가 있는 경우는 에러 케이스이므로, 제외함
            for pres_option in state.response_styles:
                if pres_option.response_style == ResponseStyle.TABLE_FETCH:
                    continue

                pres = PresentationOption(
                    response_style=pres_option.response_style,
                )
                msg.presentation.append(pres)
        return msg
