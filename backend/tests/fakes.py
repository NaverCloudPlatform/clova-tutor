# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import AsyncGenerator

from common.infra.grpc.grpc_stubs.modelchat_pb2 import (
    CreateChatTitleRequest,
    CreateChatTitleResponse,
    ModelRequest,
    ModelResponse,
    PresentationOption,
    RecommendationInfo,
)

PROBLEM_CHUNKS = [
    ModelResponse(
        id="0ce09805-c345-4ef1-bbfd-4cad9f290955",
        created=1700000000000,
        finish=False,
        model_response="좋아 문제 하나 추천해줄게",
        recommendation=RecommendationInfo(
            recommend_tool=True,
            recommended_problem_id="E3-M-001"
        ),
        presentation=[
            PresentationOption(
                response_style="recommend_problem"
            )
        ]
    ),
    ModelResponse(
        id="0ce09805-c345-4ef1-bbfd-4cad9f290955",
        created=1700000000000,
        finish=True,
        model_response="좋아 문제 하나 추천해줄게",
        recommendation=RecommendationInfo(
            recommend_tool=True,
            recommended_problem_id="E3-M-001"
        ),
        presentation=[
            PresentationOption(
                response_style="recommend_problem",
                has_translation_response=False
            )
        ]
    )
]

DEFAULT_CHUNKS = [
    ModelResponse(
        id="0ce09805-c345-4ef1-bbfd-4cad9f290955",
        created=1700000000000,
        finish=False,
        model_response="직독직해 기능은",
        recommendation=RecommendationInfo(
            recommend_tool=False,
            recommended_problem_id=""
        ),
        presentation=[
            PresentationOption(
                response_style="default_chat"
            )
        ]
    ),
    ModelResponse(
        id="0ce09805-c345-4ef1-bbfd-4cad9f290955",
        created=1700000000000,
        finish=False,
        model_response="직독직해이다.",
        recommendation=RecommendationInfo(
            recommend_tool=False,
            recommended_problem_id=""
        ),
        presentation=[
            PresentationOption(
                response_style="default_chat"
            )
        ]
    ),
    ModelResponse(
        id="0ce09805-c345-4ef1-bbfd-4cad9f290955",
        created=1700000000000,
        finish=True,
        model_response="",
        recommendation=RecommendationInfo(
            recommend_tool=False,
            recommended_problem_id=""
        ),
        presentation=[
            PresentationOption(
                response_style="default_chat"
            )
        ]
    ),
]

async def async_chunk_generator(chunks):
    for chunk in chunks:
        yield chunk

class FakeModelStreamClient:
    def __init__(self, grpc_server_url: str) -> None:
        ...

    async def create_chat_title(
        self,
        request: CreateChatTitleRequest
    ) -> CreateChatTitleResponse:
        return CreateChatTitleResponse(title="Test Created title")

    async def stream(self, request: ModelRequest) -> AsyncGenerator[ModelResponse, None]:
        print(request)
        if request.user_query == "문제 생성":
            for chunk in PROBLEM_CHUNKS:
                yield chunk

        else:
            for chunk in DEFAULT_CHUNKS:
                yield chunk

