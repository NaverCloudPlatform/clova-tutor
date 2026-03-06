# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from typing import Annotated

from typing_extensions import Doc

from common.domain.schema import CommonBase


class RecommendationInfo(CommonBase):
    recommend_tool: Annotated[bool, Doc("문제 추천 기능 사용 여부")]
    recommended_problem_id: Annotated[str, Doc("추천된 문제 ID(없으면 빈 문자열)")] = ""

class PresentationOption(CommonBase):
    response_style: Annotated[str, Doc("모델 응답 스타일 (카드, 기본 등)")]
    has_translation_response: Annotated[bool | None, Doc("직독직해 응답 형식")] = None

class AssistantResponse(CommonBase):
    id: Annotated[uuid.UUID, Doc("UUID")]
    created: Annotated[int, Doc("epoch(ms)")]
    finish: Annotated[bool, Doc("최종 메시지 여부")]
    model_response: Annotated[str, Doc("모델 응답")]
    subject: Annotated[str | None, Doc("과목명")] = None
    reference_image_document: Annotated[list[str], Doc("모델이 제공한 이미지")] = []
    recommendation: Annotated[RecommendationInfo, Doc("문제 추천 정보")]
    presentations: Annotated[list[PresentationOption], Doc("응답 스타일 + 퀴즈 버튼 노출 여부")] = []
