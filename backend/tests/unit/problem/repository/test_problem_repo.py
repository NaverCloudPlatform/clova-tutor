# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from all_models import *  # noqa: F403
from problems.database.repository import ProblemFilter, ProblemRepository
from problems.domain.problem import (
    Answer,
    GradeEnum,
    Problem,
    ProblemAnswerType,
    ProblemLevel,
    SubjectEnum,
)


@pytest.fixture
def problem_repo(db_session: AsyncSession) -> ProblemRepository:
    return ProblemRepository(session=db_session)


# -------------------------------------------------------
# upsert_many
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_upsert_many_insert_new_item(
    problem_repo: ProblemRepository,
):
    """
    1. 신규 Problem 데이터 생성
    2. upsert_many 실행
    3. DB에서 정상적으로 조회되는지 검증
    """

    # 1.
    TEST_PROBLEM = Problem(
        id="test123",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="기본 테스트 문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="정답", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )

    # 2.
    await problem_repo.upsert_many([TEST_PROBLEM])

    # 3.
    flt = ProblemFilter(id="test123")
    found = await problem_repo.find_random_problem_not_duplicated(
        flt=flt,
        exclude_ids=[],
    )

    assert found is not None
    assert found.id == "test123"
    assert found.subject == SubjectEnum.MATH


@pytest.mark.asyncio
async def test_upsert_many_update_existing_item(
    problem_repo: ProblemRepository,
):
    """
    1. 기존 Problem 데이터 삽입
    2. 동일 ID로 다른 값 upsert
    3. 변경된 값이 반영되었는지 검증
    """

    # 1.
    BASE_PROBLEM = Problem(
        id="test123",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="기본 테스트 문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="정답", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )
    await problem_repo.upsert_many([BASE_PROBLEM])

    # 2.
    UPDATED_PROBLEM = Problem(
        **BASE_PROBLEM.model_dump(
            exclude={Problem.FIELD_SUBJECT, Problem.FIELD_PROBLEM}
        ),
        subject=SubjectEnum.ENGLISH,
        problem="업데이트된 문제입니다.",
    )
    await problem_repo.upsert_many([UPDATED_PROBLEM])

    # 3.
    flt = ProblemFilter(id="test123")
    found = await problem_repo.get(flt=flt)

    assert found is not None
    assert found.subject == SubjectEnum.ENGLISH
    assert found.problem == "업데이트된 문제입니다."


# -------------------------------------------------------
# find_random_problem_not_duplicated
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_find_random_problem_not_duplicated_with_filter(
    problem_repo: ProblemRepository,
):
    """
    1. 서로 다른 subject 문제 2개 생성
    2. subject 필터로 조회
    3. 조건에 맞는 문제만 반환되는지 검증
    """

    # 1.
    PROBLEM_MATH = Problem(
        id="p_math",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="수학 문제",
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

    PROBLEM_SCIENCE = PROBLEM_MATH
    PROBLEM_SCIENCE.id = "p_science"
    PROBLEM_SCIENCE.subject = SubjectEnum.SCIENCE
    PROBLEM_SCIENCE.problem="과학 문제"

    await problem_repo.upsert_many([PROBLEM_MATH, PROBLEM_SCIENCE])

    # 2.
    flt = ProblemFilter(subject=SubjectEnum.SCIENCE)
    found = await problem_repo.find_random_problem_not_duplicated(
        flt=flt,
        exclude_ids=[],
    )

    # 3.
    assert found is not None
    assert found.id == "p_science"
    assert found.subject == SubjectEnum.SCIENCE


@pytest.mark.asyncio
async def test_find_random_problem_not_duplicated_with_exclusion(
    problem_repo: ProblemRepository,
):
    """
    1. 동일 subject 문제 2개 생성
    2. 하나를 exclude_ids로 제외
    3. 제외되지 않은 문제만 반환되는지 검증
    """

    # 1.
    PROBLEM_A = Problem(
        id="p_a",
        subject=SubjectEnum.SCIENCE,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제 A",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="A", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )
    PROBLEM_B = PROBLEM_A
    PROBLEM_B.id = "p_b"
    PROBLEM_B.problem="문제 B"

    await problem_repo.upsert_many([PROBLEM_A, PROBLEM_B])

    # 2.
    flt = ProblemFilter(subject=SubjectEnum.SCIENCE)
    found = await problem_repo.find_random_problem_not_duplicated(
        flt=flt,
        exclude_ids=["p_a"],
    )

    # 3.
    assert found is not None
    assert found.id == "p_b"


@pytest.mark.asyncio
async def test_find_random_problem_not_duplicated_returns_none_when_empty(
    problem_repo: ProblemRepository,
):
    """
    1. 조건을 만족하는 데이터가 없는 상태
    2. 조회 실행
    3. None 반환 검증
    """

    # 1.
    flt = ProblemFilter(grade=GradeEnum.ELEMENTARY_FIRST)

    # 2.
    found = await problem_repo.find_random_problem_not_duplicated(
        flt=flt,
        exclude_ids=[],
    )

    # 3.
    assert found is None
