# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


from chats.domain.assistant.assistant_request import AssistantRequest
from chats.domain.assistant.assistant_response import AssistantResponse
from common.infra.grpc.grpc_stubs.modelchat_pb2 import (
    ModelRequest,
    ModelResponse,
    PresentationOption,
    RecommendationInfo,
)


class GrpcAssistantMapper:
    @staticmethod
    def to_grpc_model(
        request: AssistantRequest
    ) -> ModelRequest:
        return ModelRequest(
            **request.model_dump(exclude={request.FIELD_USER_ID, request.FIELD_VECTOR_PROBLEM_ID, request.FIELD_REQUEST_ID}),
            vector_problem_id=None if request.vector_problem_id == "" else request.vector_problem_id,
            user_id=str(request.user_id),
            request_id=str(request.request_id)
        )


    @staticmethod
    def to_assistant_response(
        response: ModelResponse
    ) -> AssistantResponse:
        # 1) RecommendationInfo
        rec_info = RecommendationInfo(
            recommend_tool=getattr(response.recommendation, "recommend_tool", False),
            recommended_problem_id=getattr(
                response.recommendation, "recommended_problem_id", ""
            ),
        )

        # 2) PresentationOption (repeated)
        pres_opts: list[PresentationOption] = []

        for pres in response.presentation:
            pres_opt = PresentationOption(
                response_style=pres.response_style,
                has_translation_response=(
                    pres.has_translation_response
                    if pres.HasField("has_translation_response")
                    else None
                )
            )
            pres_opts.append(pres_opt)

        # 3) 상위 AssistantResponse 조립
        resp = AssistantResponse(
            id=response.id,
            created=response.created,
            finish=response.finish,
            model_response=response.model_response,
            subject=getattr(response, "subject", None),
            reference_image_document=list(
                getattr(response, "reference_image_document", [])
            ),
            recommendation=rec_info,
            presentations=pres_opts,
        )
        return resp
