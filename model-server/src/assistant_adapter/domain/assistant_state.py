# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from enum import StrEnum

from pydantic import BaseModel

from assistant.src.schema import RecommendedProblems
from assistant.src.schema import State as _RawState
from common.schema import CommonBase
from enum import StrEnum

from pydantic import BaseModel


class ResponseStyle(StrEnum):
    # 영어
    TRANSLATION = "translation"
    ENG_VOCA = "eng_voca"
    ENG_GRAMMAR = "eng_grammar"
    TABLE_FETCH = "table_fetch"
    ANSWER_INCLUDED = "answer_included"

    # 수학
    MATH_CONCEPT = "math_concept"
    STEPWISE_SOLUTION = "stepwise_solution"

    # 공통
    RECOMMEND_PROBLEM = "recommend_problem"
    DEFAULT_CHAT = "default_chat"


class ResponseStyleTool(BaseModel):
    response_style: ResponseStyle


class AssistantState(CommonBase):
    """Chat 서비스에서 실제로 활용하는 최소 필드만 가진 DTO."""

    is_final: bool = False

    model_response: str | dict | None
    subject: str | None = None
    recommend_tool: bool = False
    recommended_problem_id: str = ""
    recommended_problems: RecommendedProblems | None = None
    reference_image_document: list[str]
    response_styles: list[ResponseStyleTool] = []

    # Factory
    @classmethod
    def from_raw(cls, raw: _RawState, *, final: bool = False) -> "AssistantState":
        """assistant 패키지의 원본 State -> Adapter DTO 변환"""

        # 1. 과목 정보 추출
        subject: str | None = None
        if raw.subject_info:
            subject = raw.subject_info.subject

        # 2. response 관련 세팅
        response_styles: list[ResponseStyleTool] = []
        recommended_problem_id: str = ""

        if cur_response_info := raw.response_info:
            # recommend_problem
            if cur_response_info.recommend_problem is not None:
                recommended_problem_id = cur_response_info.recommend_problem

            for res_style in cur_response_info.response_style:
                # 모델 툴 바탕으로 BE 통신용 응답 모델 매핑
                model_res_style = ResponseStyle[str(res_style)]

                eng_table_info = cur_response_info.eng_table_info
                if (
                    model_res_style == ResponseStyle.TABLE_FETCH
                    and len(eng_table_info) > 0
                ):
                    has_eng_voca = "단어" in eng_table_info
                    has_eng_grammar = "문법" in eng_table_info

                    if has_eng_voca:
                        response_styles.append(
                            ResponseStyleTool(
                                response_style=ResponseStyle.ENG_VOCA,
                            )
                        )

                    if has_eng_grammar:
                        response_styles.append(
                            ResponseStyleTool(
                                response_style=ResponseStyle.ENG_GRAMMAR,
                            )
                        )
                else:
                    response_styles.append(
                        ResponseStyleTool(response_style=model_res_style)
                    )

        return AssistantState(
            is_final=final,
            model_response=raw.model_response,
            subject=subject,
            recommend_tool=True if recommended_problem_id != "" else False,
            recommended_problem_id=recommended_problem_id,
            recommended_problems=raw.reference_problems,
            reference_image_document=raw.image_response or [],
            response_styles=response_styles,
        )
