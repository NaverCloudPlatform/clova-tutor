# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from enum import StrEnum
from typing import Annotated

from typing_extensions import Doc, TypedDict

from common.domain.schema import CommonBase


class ReActModelToolType(StrEnum):
    # 영어
    TRANSLATION = "translation"
    ENG_VOCA = "eng_voca"
    ENG_GRAMMAR = "eng_grammar"
    TABLE_FETCH = "table_fetch"
    ANSWER_INCLUDED = "answer_included"

    # 수학
    MATH_CONCEPT = "math_concept"
    STEPWISE_SOLUTION = "stepwise_solution"
    SOLUTION_DEMONSTRATION = "solution_demonstration"

    # 공통
    RECOMMEND_PROBLEM = "recommend_problem"
    DEFAULT_CHAT = "default_chat"


class ToolValueDict(TypedDict, total=False):
    translation_button_visible: bool


class ToolInfo(CommonBase):
    name: Annotated[ReActModelToolType, Doc("모델 툴 타입 이름입니다.")]
    value: Annotated[ToolValueDict, Doc("해당 모델 툴 타입 때 보여줘야 할 값입니다.")]

# ---------------------------

class ProblemRecommended(CommonBase):
    problem_id: Annotated[int, Doc("추천된 문제 입니다.")]

# ----------------------------

class SystemHint(StrEnum):
    """시스템 힌트 플래그를 정의하는 열거형 클래스입니다.
    """
    TRANSLATION_BUTTON = "translation_button"


class ChatMessageMetadata(CommonBase):
    tools: Annotated[list[ToolInfo], Doc("모델 툴들의 리스트 형태입니다.")] = []
    problem_recommended: Annotated[ProblemRecommended | None, Doc("문제 추천 여부입니다.")] = None
    system_hints: Annotated[list[SystemHint] | None, Doc("클라이언트가 넘겨 준 모델에게 필요한 정보입니다.")] = None
