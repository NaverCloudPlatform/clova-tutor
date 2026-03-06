# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Annotated

from pydantic import BaseModel
from typing_extensions import Doc


class ProblemCreateChoiceRequest(BaseModel):
    no: int
    inst: str

class ProblemCreateAnswerRequest(BaseModel):
    answer: str
    accepted_answers: list[str] | None = None
class ProblemCreateRequest(BaseModel):
    id: str
    subject: str
    grade: int
    type: str
    level: int
    url: str | None
    semester: int | None
    primary: Annotated[str | None, Doc("대단원")]
    secondary: str | None
    specific: str | None
    category: str | None
    problem: str
    choices: list[ProblemCreateChoiceRequest] | None
    correct_answers: list[ProblemCreateAnswerRequest]
    explanation: str | None
    hint: str | None
    tags: list[str] | None

class ProblemCreateRequestBody(BaseModel):
    problems: list[ProblemCreateRequest]
