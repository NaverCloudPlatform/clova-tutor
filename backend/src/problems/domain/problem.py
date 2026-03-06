# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from enum import IntEnum, StrEnum
from typing import Annotated, ClassVar, TypeGuard

from typing_extensions import Doc

from common.domain.schema import CommonBase


class SubjectEnum(StrEnum):
    MATH = "math"
    ENGLISH = "english"
    SCIENCE = "science"


class GradeEnum(IntEnum):
    # 초등학교 (Elementary School)
    ELEMENTARY_FIRST = 1
    ELEMENTARY_SECOND = 2
    ELEMENTARY_THIRD = 3
    ELEMENTARY_FOURTH = 4
    ELEMENTARY_FIFTH = 5
    ELEMENTARY_SIXTH = 6

    # 중학교 (Middle School)
    MIDDLE_FIRST = 7
    MIDDLE_SECOND = 8
    MIDDLE_THIRD = 9

    # 고등학교 (High School)
    HIGH_FIRST = 10
    HIGH_SECOND = 11
    HIGH_THIRD = 12


class ProblemLevel(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class ProblemChoice(CommonBase):
    no: Annotated[int, Doc("선택지 번호 (1부터 시작)") ]
    inst: Annotated[str, Doc("선택지 내용 (보기 텍스트)") ]


class Answer(CommonBase):
    answer: Annotated[str, Doc("주요 정답 텍스트 또는 객관식 정답 번호(문자열)") ]
    accepted_answers: Annotated[list[str] | None, Doc("오타나 변형이 허용되는 인정 답안 목록 (채점용)") ]


class ProblemAnswerType(StrEnum):
    SINGLE_SHORT_ANSWER = "단일응답 주관식"
    MULTIPLE_SHORT_ANSWER = "다중응답 주관식"

    SINGLE_CHOICE_ANSWER = "단일선택 객관식"
    MULTIPLE_CHOICE_ANSWER = "다중선택 객관식"

class Problem(CommonBase):
    FIELD_SUBJECT: ClassVar[str] = "subject"
    FIELD_URL: ClassVar[str] = "url"
    FIELD_GRADE: ClassVar[str] = "grade"
    FIELD_SEMESTER: ClassVar[str] = "semester"
    FIELD_LEVEL: ClassVar[str] = "level"
    FIELD_PRIMARY: ClassVar[str] = "primary"
    FIELD_SECONDARY: ClassVar[str] = "secondary"
    FIELD_SPECIFIC: ClassVar[str] = "specific"
    FIELD_CATEGORY: ClassVar[str] = "category"
    FIELD_PROBLEM: ClassVar[str] = "problem"
    FIELD_CHOICES: ClassVar[str] = "choices"
    FIELD_CORRECT_ANSWERS: ClassVar[str] = "correct_answers"
    FIELD_EXPLANATION: ClassVar[str] = "explanation"
    FIELD_HINT: ClassVar[str] = "hint"
    FIELD_TAGS: ClassVar[str] = "tags"
    FIELD_TYPE: ClassVar[str] = "type"

    id: Annotated[str, Doc("문제의 고유 식별자 (DB PK)") ]
    subject: Annotated[SubjectEnum, Doc("문제의 과목 (예: MATH, ENGLISH)")]
    url: Annotated[str|None, Doc("문제 이미지 또는 원본 텍스트가 저장된 URL")]
    grade: Annotated[GradeEnum, Doc("대상 학년")]
    semester: Annotated[int | None, Doc("대상 학기 (1 또는 2, 또는 전체)")]
    level: Annotated[ProblemLevel, Doc("난이도 (1:쉬움, 2:보통, 3:어려움)")]

    primary: Annotated[str|None, Doc("대분류 (예: '수와 연산')")]
    secondary: Annotated[str|None, Doc("중분류 (예: '정수와 유리수')")]
    specific: Annotated[str|None, Doc("소분류/세부 영역 (예: '절댓값의 이해')")]

    category: Annotated[str | None, Doc("추가적인 분류 또는 출처 정보")]
    problem: Annotated[str, Doc("문제 텍스트 또는 내용")]
    choices: Annotated[list[ProblemChoice] | None ,Doc("객관식 문제의 경우 선택지 목록")]

    correct_answers:Annotated[list[Answer], Doc("문제의 정답 및 인정되는 답안 목록")]
    explanation: Annotated[str | None, Doc("문제 해설 텍스트")]
    hint: Annotated[str | None, Doc("문제 풀이 힌트 텍스트")]

    tags: Annotated[list[str] | None, Doc("문제에 할당된 키워드/태그 목록")]
    type: Annotated[ProblemAnswerType, Doc("문제의 응답 유형 (주관식/객관식, 단일/다중)")]


def is_choice_answer(problem: Problem) -> TypeGuard[Problem]:
    return problem.type in (ProblemAnswerType.SINGLE_CHOICE_ANSWER, ProblemAnswerType.MULTIPLE_CHOICE_ANSWER)


def is_short_answer(problem: Problem) -> TypeGuard[Problem]:
    return problem.type in (ProblemAnswerType.SINGLE_SHORT_ANSWER, ProblemAnswerType.MULTIPLE_SHORT_ANSWER)
