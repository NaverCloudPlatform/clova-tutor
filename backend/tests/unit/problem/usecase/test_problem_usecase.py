# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from unittest.mock import AsyncMock

import pytest

from problems.domain.problem import (
    Answer,
    GradeEnum,
    Problem,
    ProblemAnswerType,
    ProblemLevel,
    SubjectEnum,
)
from problems.presentation.schemas.request_dto import ProblemCreateRequest, ProblemCreateRequestBody
from problems.presentation.schemas.response_dto import ProblemCreateResponse, ProblemResponse
from problems.service.problem_service import ProblemService
from problems.usecase.exceptions import (
    ProblemAnswerTypeNotMatchException,
    ProblemGradeNotMatchException,
    ProblemLevelNotMatchException,
    ProblemSubjectNotMatchException,
)
from problems.usecase.problem_usecase import ProblemUseCase


@pytest.fixture
def mock_problem_service() -> AsyncMock:
    return AsyncMock(spec=ProblemService)


@pytest.fixture
def problem_use_case(mock_problem_service: AsyncMock) -> ProblemUseCase:
    return ProblemUseCase(problem_service=mock_problem_service)


# -------------------------------------------------------
# get_problem
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_problem_success(
    problem_use_case: ProblemUseCase,
    mock_problem_service: AsyncMock,
):
    """
    1. Problem 도메인 객체 생성
    2. get_problem 호출
    3. ProblemResponse 및 service 호출 검증
    """

    # 1.
    TEST_PROBLEM_ID = str(uuid.uuid4())
    TEST_PROBLEM = Problem(
        id=TEST_PROBLEM_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="테스트 문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="1", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )
    mock_problem_service.get_problem_by_id.return_value = TEST_PROBLEM

    # 2.
    response = await problem_use_case.get_problem(TEST_PROBLEM_ID)

    # 3.
    assert isinstance(response, ProblemResponse)
    assert response.root.id == TEST_PROBLEM_ID
    assert response.root.content.subject == SubjectEnum.MATH

    mock_problem_service.get_problem_by_id.assert_called_once_with(TEST_PROBLEM_ID)


# -------------------------------------------------------
# create_bulk_problems (success)
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_bulk_problems_success(
    problem_use_case: ProblemUseCase,
    mock_problem_service: AsyncMock,
):
    """
    1. ProblemCreateRequest 2개 생성
    2. create_bulk_problems 호출
    3. 반환값 및 create_problems 호출 인자 검증
    """

    # 1.
    TEST_REQ_EN = ProblemCreateRequest.model_validate(
        {
            "id": "E3-E-001",
            "subject": "english",
            "grade": 3,
            "type": "단일선택 객관식",
            "category": "파닉스",
            "level": 2,
            "url": None,
            "semester": None,
            "primary": "소리",
            "secondary": "파닉스",
            "specific": "단자음",
            "problem": "map?",
            "choices": [{"no": 1, "inst": "map"}],
            "correct_answers": [{"answer": "1", "accepted_answers": None}],
            "explanation": "설명",
            "hint": "힌트",
            "tags": ["m"],
        }
    )

    TEST_REQ_MATH = ProblemCreateRequest.model_validate(
        {
            "id": "E3-M-001",
            "subject": "math",
            "grade": 3,
            "type": "단일응답 주관식",
            "category": "덧셈",
            "level": 1,
            "url": None,
            "semester": None,
            "primary": "수",
            "secondary": "덧셈",
            "specific": "세 자리",
            "problem": "1+1?",
            "choices": None,
            "correct_answers": [{"answer": "2", "accepted_answers": None}],
            "explanation": "설명",
            "hint": "힌트",
            "tags": ["덧셈"],
        }
    )

    CREATED_PROBLEMS = [
        Problem(
            **TEST_REQ_EN.model_dump(exclude={"subject", "grade", "level", "type"}),
            subject=SubjectEnum.ENGLISH,
            grade=GradeEnum(TEST_REQ_EN.grade),
            level=ProblemLevel(TEST_REQ_EN.level),
            type=ProblemAnswerType(TEST_REQ_EN.type),
        ),
        Problem(
            **TEST_REQ_MATH.model_dump(exclude={"subject", "grade", "level", "type"}),
            subject=SubjectEnum.MATH,
            grade=GradeEnum(TEST_REQ_MATH.grade),
            level=ProblemLevel(TEST_REQ_MATH.level),
            type=ProblemAnswerType(TEST_REQ_MATH.type),
        ),
    ]
    mock_problem_service.create_problems.return_value = CREATED_PROBLEMS

    BODY = ProblemCreateRequestBody(problems=[TEST_REQ_EN, TEST_REQ_MATH])

    # 2.
    response = await problem_use_case.create_bulk_problems(body=BODY)

    # 3.
    assert isinstance(response, ProblemCreateResponse)
    assert set(response.ids) == {p.id for p in CREATED_PROBLEMS}

    mock_problem_service.create_problems.assert_called_once()
    args, _ = mock_problem_service.create_problems.call_args
    assert len(args[0]) == 2
    assert args[0][0].subject == SubjectEnum.ENGLISH
    assert args[0][1].subject == SubjectEnum.MATH


# -------------------------------------------------------
# create_bulk_problems (invalid subject)
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_bulk_problems_invalid_subject(
    problem_use_case: ProblemUseCase,
):
    """
    1. 잘못된 subject 요청 생성
    2. create_bulk_problems 호출
    3. ProblemSubjectNotMatchException 발생 검증
    """

    # 1.
    TEST_REQ = ProblemCreateRequest.model_validate(
        {
        "id": "E3-M-001",
        "subject": "TEST!@#!@#@!",
        "grade": 3,
        "type": "단일응답 주관식",
        "level": 1,
        "url": None,
        "semester": None,
        "primary": "수와 연산",
        "secondary": "덧셈",
        "specific": "세 자리 수",
        "category": "덧셈",
        "problem": "345 + 276 = ?",
        "choices": None,
        "correct_answers": [
            {
                "answer": "621",
                "accepted_answers": ["621.", "621 "]
            }
        ],
        "explanation": "345와 276을 더하면 621입니다.",
        "hint": "일의 자리부터 계산하세요.",
        "tags": ["덧셈", "세 자리 수"],
    }
    )

    # 2. & 3.
    with pytest.raises(ProblemSubjectNotMatchException):
        await problem_use_case.create_bulk_problems(
            body=ProblemCreateRequestBody(problems=[TEST_REQ])
        )


# -------------------------------------------------------
# create_bulk_problems (invalid grade)
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_bulk_problems_invalid_grade(
    problem_use_case: ProblemUseCase,
):
    """
    1. 잘못된 grade 요청 생성
    2. create_bulk_problems 호출
    3. ProblemGradeNotMatchException 발생 검증
    """

    # 1.
    TEST_REQ = ProblemCreateRequest.model_validate(
        {
            "id": "E3-M-001",
            "subject": "math",
            "grade": 999,
            "type": "단일응답 주관식",
            "level": 1,
            "url": None,
            "semester": None,
            "primary": "수와 연산",
            "secondary": "덧셈",
            "specific": "세 자리 수",
            "category": "덧셈",
            "problem": "345 + 276 = ?",
            "choices": None,
            "correct_answers": [
                {
                    "answer": "621",
                    "accepted_answers": ["621.", "621 "]
                }
            ],
            "explanation": "345와 276을 더하면 621입니다.",
            "hint": "일의 자리부터 계산하세요.",
            "tags": ["덧셈", "세 자리 수"],
        }
    )

    # 2. & 3.
    with pytest.raises(ProblemGradeNotMatchException):
        await problem_use_case.create_bulk_problems(
            body=ProblemCreateRequestBody(problems=[TEST_REQ])
        )


# -------------------------------------------------------
# create_bulk_problems (invalid level)
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_bulk_problems_invalid_level(
    problem_use_case: ProblemUseCase,
):
    """
    1. 잘못된 level 요청 생성
    2. create_bulk_problems 호출
    3. ProblemLevelNotMatchException 발생 검증
    """

    # 1.
    TEST_REQ = ProblemCreateRequest.model_validate(
        {
            "id": "E3-M-001",
            "subject": "math",
            "grade": 3,
            "type": "단일응답 주관식",
            "level": 999,
            "url": None,
            "semester": None,
            "primary": "수와 연산",
            "secondary": "덧셈",
            "specific": "세 자리 수",
            "category": "덧셈",
            "problem": "345 + 276 = ?",
            "choices": None,
            "correct_answers": [
                {
                    "answer": "621",
                    "accepted_answers": ["621.", "621 "]
                }
            ],
            "explanation": "345와 276을 더하면 621입니다.",
            "hint": "일의 자리부터 계산하세요.",
            "tags": ["덧셈", "세 자리 수"],
        }
    )

    # 2. & 3.
    with pytest.raises(ProblemLevelNotMatchException):
        await problem_use_case.create_bulk_problems(
            body=ProblemCreateRequestBody(problems=[TEST_REQ])
        )


# -------------------------------------------------------
# create_bulk_problems (invalid answer type)
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_bulk_problems_invalid_answer_type(
    problem_use_case: ProblemUseCase,
):
    """
    1. 잘못된 answer type 요청 생성
    2. create_bulk_problems 호출
    3. ProblemAnswerTypeNotMatchException 발생 검증
    """

    # 1.
    TEST_REQ = ProblemCreateRequest.model_validate(
        {
            "id": "E3-M-001",
            "subject": "math",
            "grade": 3,
            "type": "테스트 문제",
            "level": 1,
            "url": None,
            "semester": None,
            "primary": "수와 연산",
            "secondary": "덧셈",
            "specific": "세 자리 수",
            "category": "덧셈",
            "problem": "345 + 276 = ?",
            "choices": None,
            "correct_answers": [
                {
                    "answer": "621",
                    "accepted_answers": ["621.", "621 "]
                }
            ],
            "explanation": "345와 276을 더하면 621입니다.",
            "hint": "일의 자리부터 계산하세요.",
            "tags": ["덧셈", "세 자리 수"],
        }
    )

    # 2. & 3.
    with pytest.raises(ProblemAnswerTypeNotMatchException):
        await problem_use_case.create_bulk_problems(
            body=ProblemCreateRequestBody(problems=[TEST_REQ])
        )
