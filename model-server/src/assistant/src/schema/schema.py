# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import os
from typing import Annotated, ClassVar, Optional, Union

from langgraph.graph.message import add_messages
from omegaconf import OmegaConf
from pydantic import BaseModel, Field, field_validator

from assistant.src.mapping import ErrorType, ResponseStyleMapEng, ResponseStyleMapMath
from config.config import model_config


class ModelParam(BaseModel):
    model: Optional[str] = "hcx-005"
    max_tokens: Optional[int] = 2048
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    repeat_penalty: Optional[float] = None
    stop: Optional[list[str]] = None

    VALID_MODELS: ClassVar[set] = {
        "hcx-005",
        "gpt-4o",
    }

    # Load config
    current_dir: ClassVar[str] = os.path.dirname(os.path.abspath(__file__))
    default_model_options: ClassVar[dict] = OmegaConf.load(
        os.path.join(model_config.MODEL_OPTION, "default_model_options.yaml")
    )

    @field_validator("model")
    @classmethod
    def validate_model(cls, value):
        if value not in cls.VALID_MODELS:
            raise ValueError(
                f"Invalid model name: {value}. Must be one of {cls.VALID_MODELS}"
            )
        return value

    def __init__(self, **data):
        model_name = data.get("model", "hcx-005")
        if model_name in self.default_model_options:
            base_options = self.default_model_options[model_name]
            final_options = {**base_options, **data}  # 사용자 입력 우선
        else:
            final_options = data

        if model_name == "gpt-4o":
            allowed_keys = {"model", "max_tokens", "temperature"}
            final_options = {
                k: v for k, v in final_options.items() if k in allowed_keys
            }
        super().__init__(**final_options)


class StudentProfile(BaseModel):
    user_id: str
    name: str = "김철수"
    semester: Optional[int] = None
    grade: int


class SubjectInfo(BaseModel):
    subject: str
    section: Optional[str] = ""
    unit: Optional[Union[list[str], str]] = ""
    topic: Optional[list[str]] = None
    is_generated: bool = False


class UnknownConcept(BaseModel):
    subject: str
    key_concept: str = ""
    unknown_concept: Optional[list[str]] = None
    unknown_concept_reason: str = ""


class Explanation(BaseModel):
    text: dict = {}
    is_generated: bool = False


class Answer(BaseModel):
    text: str
    is_generated: bool = False


class ProblemInfo(BaseModel):
    problem_id: Optional[str] = ""
    question: str
    explanation: Optional[Explanation] = None
    answer: Optional[Answer] = None
    level: Optional[int] = None
    subject_info: SubjectInfo
    data_source: Optional[str] = ""
    has_image: Optional[bool] = False
    image_url: Optional[str] = ""


class ProblemHistory(ProblemInfo):
    context: str
    keywords: list[str]


class ReferenceProblemInfo(BaseModel):
    problem_info: ProblemInfo
    similarity_score: float


class RecommendedProblems(BaseModel):
    easy: list[ReferenceProblemInfo]
    normal: list[ReferenceProblemInfo]
    hard: list[ReferenceProblemInfo]


class Context(BaseModel):
    is_related: bool
    model_response: str


class Error(BaseModel):
    type: Optional[ErrorType] = None
    error_msg: str = ""
    node_name: str = ""
    file_name: str = ""
    line: int = 0
    model_param: Optional[ModelParam] = None


class ResponseInfo(BaseModel):
    response_style: set[Union[ResponseStyleMapEng, ResponseStyleMapMath]] = Field(
        default_factory=set
    )
    eng_table_info: set[str] = Field(default_factory=set)
    more_difficult: Optional[bool] = None
    reason: Optional[str] = ""
    recommend_problem: Optional[str] = ""
    no_problems_reason: Optional[str] = None  # "no_data" or "all_filtered"
    usage: dict = {}


class State(BaseModel):
    # need to maintain
    messages: Annotated[list, add_messages]
    problem_info: Optional[ProblemInfo] = None
    problem_history: Optional[list[ProblemHistory]] = []
    subject_info: Optional[SubjectInfo] = None
    parent_run_id: Optional[str] = None  # LangGraph compatibility

    # BE input
    db_problem_id: Optional[str] = None

    # output-related, need to initialize
    response_info: Optional[ResponseInfo] = None
    model_response: Optional[Union[str, dict]] = None
    table_response: Optional[Union[str, list]] = None
    translation_response: Optional[str] = None
    image_response: Optional[list] = None
    error: Optional[Error] = None

    # need to initialize
    reference_document: Optional[list] = None
    reference_problems: Optional[RecommendedProblems] = None
    recommended_problem_ids: list[str] = Field(
        default_factory=list
    )  # Track all recommended problems in session
    level_instruction: Optional[bool] = None


class BinaryOutput(BaseModel):
    result: bool = Field(
        description="요청에 대한 답변을 true 또는 false로 반환합니다.",
        json_schema_extra={"required": True},
    )
