# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from goals.database.repository import GoalFilter, GoalRepository
from goals.domain.goal import Goal, GoalStatus
from problems.domain.problem import SubjectEnum


@pytest.fixture
def goal_repo(db_session: AsyncSession) -> GoalRepository:
    return GoalRepository(session=db_session)


# -----------------------------------------------------
# exists
# -----------------------------------------------------
@pytest.mark.asyncio
async def test_exists_true_by_id(
    goal_repo: GoalRepository,
):
    """
    1. Goal 생성
    2. id 기준 exists 호출
    3. True 반환 검증
    """

    # 1.
    TEST_GOAL = await goal_repo.create(
        Goal(
            subject=SubjectEnum.SCIENCE,
            user_id=uuid.uuid4(),
            chat_id=-1,
            goal_count=15,
            solved_count=0,
            status=GoalStatus.ACTIVE,
        )
    )

    # 2.
    exists_found = await goal_repo.exists(
        flt=GoalFilter(id=TEST_GOAL.id)
    )

    # 3.
    assert exists_found is True


@pytest.mark.asyncio
async def test_exists_false_for_unknown_id(
    goal_repo: GoalRepository,
):
    """
    1. 존재하지 않는 id 준비
    2. exists 호출
    3. False 반환 검증
    """

    # 1.
    UNKNOWN_ID = uuid.uuid4()

    # 2.
    exists_found = await goal_repo.exists(
        flt=GoalFilter(id=UNKNOWN_ID)
    )

    # 3.
    assert exists_found is False


@pytest.mark.asyncio
async def test_exists_with_user_and_subject(
    goal_repo: GoalRepository,
):
    """
    1. 특정 user_id + subject Goal 생성
    2. 동일 조건으로 exists 호출
    3. True 반환 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    await goal_repo.create(
        Goal(
            subject=SubjectEnum.ENGLISH,
            user_id=TEST_USER_ID,
            chat_id=12345,
            goal_count=10,
            solved_count=0,
            status=GoalStatus.ACTIVE,
        )
    )

    # 2.
    exists_found = await goal_repo.exists(
        flt=GoalFilter(
            user_id=TEST_USER_ID,
            subject=SubjectEnum.ENGLISH,
        )
    )

    # 3.
    assert exists_found is True


@pytest.mark.asyncio
async def test_exists_with_status_filter(
    goal_repo: GoalRepository,
):
    """
    1. COMPLETED 상태 Goal 생성
    2. status 기준 exists 호출
    3. True 반환 검증
    """

    # 1.
    await goal_repo.create(
        Goal(
            subject=SubjectEnum.MATH,
            user_id=uuid.uuid4(),
            chat_id=55555,
            goal_count=7,
            solved_count=0,
            status=GoalStatus.COMPLETED,
        )
    )

    # 2.
    exists_found = await goal_repo.exists(
        flt=GoalFilter(status=GoalStatus.COMPLETED)
    )

    # 3.
    assert exists_found is True


@pytest.mark.asyncio
async def test_exists_with_multiple_goals(
    goal_repo: GoalRepository,
):
    """
    1. 서로 다른 user / subject Goal 2개 생성
    2. 다양한 조건으로 exists 호출
    3. 조건별 True / False 검증
    """

    # 1.
    USER_A = uuid.uuid4()
    USER_B = uuid.uuid4()

    await goal_repo.create(
        Goal(
            subject=SubjectEnum.ENGLISH,
            user_id=USER_A,
            chat_id=1111,
            goal_count=5,
            solved_count=0,
            status=GoalStatus.ACTIVE,
        )
    )

    await goal_repo.create(
        Goal(
            subject=SubjectEnum.MATH,
            user_id=USER_B,
            chat_id=2222,
            goal_count=8,
            solved_count=0,
            status=GoalStatus.ACTIVE,
        )
    )

    # 2. & 3.
    assert await goal_repo.exists(
        flt=GoalFilter(user_id=USER_A, subject=SubjectEnum.ENGLISH)
    ) is True

    assert await goal_repo.exists(
        flt=GoalFilter(user_id=USER_A, subject=SubjectEnum.MATH)
    ) is False

    assert await goal_repo.exists(
        flt=GoalFilter(user_id=USER_B, subject=SubjectEnum.ENGLISH)
    ) is False
