# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Annotated, Literal

from pydantic import Field, RootModel

from common.domain.schema import CommonBase
from problems.domain.problem import ProblemAnswerType


class ProblemCommonResponse(CommonBase):
    subject: str
    grade: int
    semester: int | None
    level: int

    primary: str | None
    secondary: str | None
    specific: str | None

    category: str | None
    problem: str
    tags: list[str] | None = None

    hint: str | None
    explanation: str | None


class ProblemChoice(CommonBase):
    no: int
    inst: str


class ChoiceProblemContent(ProblemCommonResponse):
    choices: list[ProblemChoice] = []


class ShortAnswerProblemContent(ProblemCommonResponse):
    ...


class SingleChoiceProblemResponse(CommonBase):
    id: str
    type: Literal[ProblemAnswerType.SINGLE_CHOICE_ANSWER]
    content: ChoiceProblemContent

class MultipleChoiceProblemResponse(CommonBase):
    id: str
    type: Literal[ProblemAnswerType.MULTIPLE_CHOICE_ANSWER]
    content: ChoiceProblemContent

class SingleShortAnswerProblemResponse(CommonBase):
    id: str
    type: Literal[ProblemAnswerType.SINGLE_SHORT_ANSWER]
    content: ShortAnswerProblemContent

class MultipleShortAnswerProblemResponse(CommonBase):
    id: str
    type: Literal[ProblemAnswerType.MULTIPLE_SHORT_ANSWER]
    content: ShortAnswerProblemContent


ProblemDetail = Annotated[
    SingleChoiceProblemResponse | MultipleChoiceProblemResponse | SingleShortAnswerProblemResponse | MultipleShortAnswerProblemResponse,
    Field(discriminator="type")
]

class ProblemResponse(RootModel[ProblemDetail]):
    ...



class ProblemCreateResponse(CommonBase):
    ids: list[str]
