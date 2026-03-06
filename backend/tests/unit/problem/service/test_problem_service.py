# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from unittest.mock import AsyncMock

import pytest

from problems.database.repository import ProblemFilter, ProblemRepository
from problems.domain.problem import (
    Answer,
    GradeEnum,
    Problem,
    ProblemAnswerType,
    ProblemLevel,
    SubjectEnum,
)
from problems.service.exceptions import ProblemNotFoundException
from problems.service.problem_service import ProblemService


@pytest.fixture
def mock_problem_repository() -> AsyncMock:
    return AsyncMock(spec=ProblemRepository)


@pytest.fixture
def problem_service(mock_problem_repository: AsyncMock) -> ProblemService:
    return ProblemService(problem_repo=mock_problem_repository)


# -------------------------------------------------------
# get_problems_by_subject_and_grade
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_problems_by_subject_and_grade(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. 조회용 Problem 데이터 생성
    2. get_problems_by_subject_and_grade 호출
    3. 반환값 및 repository 호출 검증
    """

    # 1.
    TEST_SUBJECT = SubjectEnum.MATH
    TEST_GRADE = GradeEnum.HIGH_FIRST
    TEST_PROBLEM = Problem(
        id="p1",
        subject=TEST_SUBJECT,
        grade=TEST_GRADE,
        problem="문제",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )
    mock_problem_repository.get_list.return_value = [TEST_PROBLEM]

    # 2.
    problems = await problem_service.get_problems_by_subject_and_grade(
        subject=TEST_SUBJECT,
        grade=TEST_GRADE,
    )

    # 3.
    assert len(problems) == 1
    assert problems[0].id == "p1"

    mock_problem_repository.get_list.assert_called_once()
    _, kwargs = mock_problem_repository.get_list.call_args
    flt = kwargs["flt"]
    assert isinstance(flt, ProblemFilter)
    assert flt.subject == TEST_SUBJECT
    assert flt.grade == TEST_GRADE


# -------------------------------------------------------
# get_problem_by_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_problem_by_id_success(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. repository.get 반환값 설정
    2. get_problem_by_id 호출
    3. 정상 반환 검증
    """

    # 1.
    TEST_ID = "test123"
    TEST_PROBLEM = Problem(
        id=TEST_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )
    mock_problem_repository.get.return_value = TEST_PROBLEM

    # 2.
    result = await problem_service.get_problem_by_id(TEST_ID)

    # 3.
    assert result.id == TEST_ID

    mock_problem_repository.get.assert_called_once()
    _, kwargs = mock_problem_repository.get.call_args
    assert isinstance(kwargs["flt"], ProblemFilter)
    assert kwargs["flt"].id == TEST_ID


@pytest.mark.asyncio
async def test_get_problem_by_id_not_found(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. repository.get None 반환 설정
    2. get_problem_by_id 호출
    3. ProblemNotFoundException 발생 검증
    """

    # 1.
    TEST_ID = str(uuid.uuid4())
    mock_problem_repository.get.return_value = None

    # 2.
    with pytest.raises(ProblemNotFoundException):
        await problem_service.get_problem_by_id(TEST_ID)

    # 3.
    mock_problem_repository.get.assert_called_once()


# -------------------------------------------------------
# get_problems_by_ids
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_problems_by_ids(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. ID 목록 및 Problem 데이터 생성
    2. get_problems_by_ids 호출
    3. 반환값 및 filter 검증
    """

    # 1.
    TEST_PROBLEM_1 = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제1",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )
    TEST_PROBLEM_2 = Problem(
        id="p2",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제2",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )
    mock_problem_repository.get_list.return_value = [TEST_PROBLEM_1, TEST_PROBLEM_2]

    # 2.
    results = await problem_service.get_problems_by_ids(["p1", "p2"])

    # 3.
    assert {p.id for p in results} == {"p1", "p2"}

    mock_problem_repository.get_list.assert_called_once()
    _, kwargs = mock_problem_repository.get_list.call_args
    assert set(kwargs["flt"].id) == {"p1", "p2"}


# -------------------------------------------------------
# find_random_problem
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_find_random_problem_with_filters(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. repository 반환값 설정
    2. find_random_problem 호출
    3. 필터 전달 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )
    mock_problem_repository.find_random_problem_not_duplicated.return_value = TEST_PROBLEM

    # 2.
    result = await problem_service.find_random_problem(
        exclude_ids=["x", "y"],
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        semester=1,
    )

    # 3.
    assert result == TEST_PROBLEM

    mock_problem_repository.find_random_problem_not_duplicated.assert_called_once()
    _, kwargs = mock_problem_repository.find_random_problem_not_duplicated.call_args
    assert kwargs["exclude_ids"] == ["x", "y"]
    assert isinstance(kwargs["flt"], ProblemFilter)


@pytest.mark.asyncio
async def test_find_random_problem_not_found(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. repository None 반환 설정
    2. find_random_problem 호출
    3. None 반환 검증
    """

    # 1.
    mock_problem_repository.find_random_problem_not_duplicated.return_value = None

    # 2.
    result = await problem_service.find_random_problem(exclude_ids=[])

    # 3.
    assert result is None
    mock_problem_repository.find_random_problem_not_duplicated.assert_called_once()


# -------------------------------------------------------
# create_problems
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_problems(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. Problem 목록 생성
    2. create_problems 호출
    3. upsert_many 및 조회 검증
    """

    # 1.
    TEST_PROBLEM_1 = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제1",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )

    TEST_PROBLEM_2 = Problem(
        id="p2",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제2",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )

    mock_problem_repository.get_list.return_value = [TEST_PROBLEM_1, TEST_PROBLEM_2]

    # 2.
    results = await problem_service.create_problems([TEST_PROBLEM_1, TEST_PROBLEM_2])

    # 3.
    assert {p.id for p in results} == {"p1", "p2"}
    mock_problem_repository.upsert_many.assert_called_once()
    mock_problem_repository.get_list.assert_called_once()


# -------------------------------------------------------
# submit_problem_answer
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_submit_problem_answer_choice_correct(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. 선택형 Problem 설정
    2. submit_problem_answer 호출
    3. True 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )
    mock_problem_repository.get.return_value = TEST_PROBLEM

    # 2.
    result = await problem_service.submit_problem_answer("p1", 1)

    # 3.
    assert result is True
    mock_problem_repository.get.assert_called_once()


@pytest.mark.asyncio
async def test_submit_problem_answer_short_answer_incorrect(
    problem_service: ProblemService,
    mock_problem_repository: AsyncMock,
):
    """
    1. 단답형 Problem 설정
    2. submit_problem_answer 호출
    3. False 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="10", accepted_answers=["열"])],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )
    mock_problem_repository.get.return_value = TEST_PROBLEM

    # 2.
    result = await problem_service.submit_problem_answer("p1", "9")

    # 3.
    assert result is False
    mock_problem_repository.get.assert_called_once()


# -------------------------------------------------------
# _check_choice_answer
# -------------------------------------------------------
def test_check_single_choice_answer_int_correct(problem_service: ProblemService):
    """
    1. 단일 선택형 Problem 생성
    2. int 정답 제출
    3. True 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )

    # 2.
    result = problem_service._check_choice_answer(TEST_PROBLEM, 1)

    # 3.
    assert result is True


def test_check_single_choice_answer_list_correct(problem_service: ProblemService):
    """
    1. 단일 선택형 Problem 생성
    2. list[int] 정답 제출
    3. True 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )

    # 2.
    result = problem_service._check_choice_answer(TEST_PROBLEM, [1])

    # 3.
    assert result is True


def test_check_single_choice_answer_incorrect(problem_service: ProblemService):
    """
    1. 단일 선택형 Problem 생성
    2. 오답 제출
    3. False 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
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
        type=ProblemAnswerType.SINGLE_CHOICE_ANSWER,
        semester=1,
    )

    # 2.
    assert problem_service._check_choice_answer(TEST_PROBLEM, 2) is False
    assert problem_service._check_choice_answer(TEST_PROBLEM, [1, 2]) is False


def test_check_multiple_choice_answer_correct(problem_service: ProblemService):
    """
    1. 복수 선택형 Problem 생성
    2. 정답 제출
    3. True 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[
            Answer(answer="2", accepted_answers=None),
            Answer(answer="4", accepted_answers=None),
        ],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.MULTIPLE_CHOICE_ANSWER,
        semester=1,
    )

    # 2.
    assert problem_service._check_choice_answer(TEST_PROBLEM, [2, 4]) is True
    assert problem_service._check_choice_answer(TEST_PROBLEM, [4, 2]) is True


def test_check_multiple_choice_answer_incorrect(problem_service: ProblemService):
    """
    1. 복수 선택형 Problem 생성
    2. 오답 제출
    3. False 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[
            Answer(answer="2", accepted_answers=None),
            Answer(answer="4", accepted_answers=None),
        ],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.MULTIPLE_CHOICE_ANSWER,
        semester=1,
    )

    # 2.
    assert problem_service._check_choice_answer(TEST_PROBLEM, [2]) is False
    assert problem_service._check_choice_answer(TEST_PROBLEM, [1, 2, 4]) is False


# -------------------------------------------------------
# _check_short_answer
# -------------------------------------------------------
def test_check_single_short_answer_exact_correct(problem_service: ProblemService):
    """
    1. 단일 단답형 Problem 생성
    2. 정확한 정답 제출
    3. True 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="10", accepted_answers=["열", "ten"])],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )

    # 2.
    assert problem_service._check_short_answer(TEST_PROBLEM, "10") is True
    assert problem_service._check_short_answer(TEST_PROBLEM, "열") is True
    assert problem_service._check_short_answer(TEST_PROBLEM, "ten") is True


def test_check_single_short_answer_incorrect(problem_service: ProblemService):
    """
    1. 단일 단답형 Problem 생성
    2. 오답 제출
    3. False 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="10", accepted_answers=["열"])],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )

    # 2.
    assert problem_service._check_short_answer(TEST_PROBLEM, "9") is False
    assert problem_service._check_short_answer(TEST_PROBLEM, ["10"]) is False


def test_check_multiple_short_answer_correct(problem_service: ProblemService):
    """
    1. 복수 단답형 Problem 생성
    2. 정답 제출
    3. True 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[
            Answer(answer="사과", accepted_answers=None),
            Answer(answer="바나나", accepted_answers=["banana"]),
        ],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.MULTIPLE_SHORT_ANSWER,
        semester=1,
    )

    # 2.
    assert problem_service._check_short_answer(TEST_PROBLEM, ["사과", "바나나"]) is True
    assert problem_service._check_short_answer(TEST_PROBLEM, ["바나나", "banana"]) is False


def test_check_multiple_short_answer_incorrect(problem_service: ProblemService):
    """
    1. 복수 단답형 Problem 생성
    2. 오답 제출
    3. False 반환 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="p1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[
            Answer(answer="사과", accepted_answers=None),
            Answer(answer="바나나", accepted_answers=["banana"]),
        ],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.MULTIPLE_SHORT_ANSWER,
        semester=1,
    )

    # 2.
    assert problem_service._check_short_answer(TEST_PROBLEM, ["사과"]) is False
    assert problem_service._check_short_answer(TEST_PROBLEM, ["사과", "배"]) is False
    assert problem_service._check_short_answer(TEST_PROBLEM, ["사과", "바나나", "딸기"]) is False
    assert problem_service._check_short_answer(TEST_PROBLEM, "사과") is False
