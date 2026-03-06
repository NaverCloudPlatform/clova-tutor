# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from goals.database.models import GoalModel
from goals.database.repository import GoalFilter, GoalRepository
from goals.domain.goal import Goal, GoalStatus
from goals.service.exceptions import InvalidGoalValueExeception, NotFoundGoalException
from goals.service.goal_service import GoalService
from problems.domain.problem import SubjectEnum


@pytest.fixture
def mock_goal_repository() -> AsyncMock:
    return AsyncMock(spec=GoalRepository)


@pytest.fixture
def goal_service(mock_goal_repository: AsyncMock) -> GoalService:
    return GoalService(goal_repository=mock_goal_repository)


# -------------------------------------------------------
# exists_by_chat_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_exists_by_chat_id_true(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. repository.exists → True 설정
    2. exists_by_chat_id 호출
    3. True 반환 + GoalFilter 인자 검증
    """

    # 1.
    mock_goal_repository.exists.return_value = True

    # 2.
    result = await goal_service.exists_by_chat_id(
        chat_id=123,
        status=GoalStatus.ACTIVE,
    )

    # 3.
    assert result is True

    mock_goal_repository.exists.assert_called_once()
    _, kwargs = mock_goal_repository.exists.call_args
    assert isinstance(kwargs["flt"], GoalFilter)
    assert kwargs["flt"].chat_id == 123
    assert kwargs["flt"].status == GoalStatus.ACTIVE


@pytest.mark.asyncio
async def test_exists_by_chat_id_false(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. repository.exists → False 설정
    2. exists_by_chat_id 호출
    3. False 반환 검증
    """

    # 1.
    mock_goal_repository.exists.return_value = False

    # 2.
    result = await goal_service.exists_by_chat_id(chat_id=456)

    # 3.
    assert result is False
    mock_goal_repository.exists.assert_called_once()


# -------------------------------------------------------
# create_goal
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_goal_success(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. create 반환 Goal 설정
    2. create_goal 호출
    3. Goal 반환 + 생성 인자 검증
    """

    # 1.
    TEST_USER_ID = uuid4()
    mock_goal_repository.create.return_value = Goal(
        id=10,
        user_id=TEST_USER_ID,
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=5,
        solved_count=0,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )

    # 2.
    result = await goal_service.create_goal(
        user_id=TEST_USER_ID,
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=5,
    )

    # 3.
    assert isinstance(result, Goal)
    assert result.goal_count == 5

    mock_goal_repository.create.assert_called_once()
    created_goal = mock_goal_repository.create.call_args.args[0]
    assert created_goal.user_id == TEST_USER_ID
    assert created_goal.subject == SubjectEnum.MATH


# -------------------------------------------------------
# get_goal_by_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_goal_by_id_success(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. repository.get → Goal 반환
    2. get_goal_by_id 호출
    3. Goal 반환 + 필터 id 검증
    """

    # 1.
    mock_goal_repository.get.return_value = Goal(
        id=10,
        user_id=uuid4(),
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=3,
        solved_count=0,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )

    # 2.
    result = await goal_service.get_goal_by_id(goal_id=10)

    # 3.
    assert isinstance(result, Goal)
    mock_goal_repository.get.assert_called_once()
    _, kwargs = mock_goal_repository.get.call_args
    assert kwargs["flt"].id == 10


@pytest.mark.asyncio
async def test_get_goal_by_id_not_found(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. repository.get → None
    2. get_goal_by_id 호출
    3. NotFoundGoalException 발생
    """

    # 1.
    mock_goal_repository.get.return_value = None

    # 2. & 3.
    with pytest.raises(NotFoundGoalException):
        await goal_service.get_goal_by_id(goal_id=99)


# -------------------------------------------------------
# get_goal_by_chat_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_goal_by_chat_id_success(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. repository.get → Goal 반환
    2. get_goal_by_chat_id 호출
    3. chat_id 검증
    """

    # 1.
    mock_goal_repository.get.return_value = Goal(
        id=3,
        user_id=uuid4(),
        chat_id=123,
        subject=SubjectEnum.ENGLISH,
        goal_count=4,
        solved_count=0,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )

    # 2.
    result = await goal_service.get_goal_by_chat_id(123)

    # 3.
    assert result.chat_id == 123
    mock_goal_repository.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_goal_by_chat_id_not_found(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. repository.get → None
    2. get_goal_by_chat_id 호출
    3. NotFoundGoalException 발생
    """

    # 1.
    mock_goal_repository.get.return_value = None

    # 2. & 3.
    with pytest.raises(NotFoundGoalException):
        await goal_service.get_goal_by_chat_id(321)


# -------------------------------------------------------
# list_goal_by_chat_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_list_goal_by_chat_id(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. get_list 반환 목록 설정
    2. list_goal_by_chat_id 호출
    3. 동일 리스트 반환 검증
    """

    # 1.
    goals = [
        Goal(
            id=1,
            user_id=uuid4(),
            chat_id=10,
            subject=SubjectEnum.MATH,
            goal_count=3,
            solved_count=0,
            status=GoalStatus.ACTIVE,
            finished_at=None,
        )
    ]
    mock_goal_repository.get_list.return_value = goals

    # 2.
    result = await goal_service.list_goal_by_chat_id(10)

    # 3.
    assert result == goals
    mock_goal_repository.get_list.assert_called_once()


# -------------------------------------------------------
# change_goal_status
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_change_goal_status_success(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. GoalModel(status=ACTIVE) 반환
    2. change_goal_status 호출
    3. COMPLETED로 변경 검증
    """

    # 1.
    goal_model = MagicMock(spec=GoalModel)
    goal_model.status = GoalStatus.ACTIVE

    mock_goal_repository.get.return_value = goal_model
    mock_goal_repository.update_from_model.return_value = Goal(
        id=1,
        user_id=uuid4(),
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=3,
        solved_count=0,
        status=GoalStatus.COMPLETED,
        finished_at=None,
    )

    # 2.
    result = await goal_service.change_goal_status(1, GoalStatus.COMPLETED)

    # 3.
    assert result.status == GoalStatus.COMPLETED
    mock_goal_repository.update_from_model.assert_called_once()


@pytest.mark.asyncio
async def test_change_goal_status_not_found(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. repository.get → None
    2. change_goal_status 호출
    3. NotFoundGoalException 발생
    """

    # 1.
    mock_goal_repository.get.return_value = None

    # 2. & 3.
    with pytest.raises(NotFoundGoalException):
        await goal_service.change_goal_status(1, GoalStatus.COMPLETED)


@pytest.mark.asyncio
async def test_change_goal_status_same(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. 기존 status == 요청 status
    2. update 없이 convert 결과 반환
    3. update_from_model 호출되지 않음
    """

    # 1.
    goal_model = MagicMock(spec=GoalModel)
    goal_model.status = GoalStatus.ACTIVE
    mock_goal_repository.get.return_value = goal_model

    converted_goal = Goal(
        id=1,
        user_id=uuid4(),
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=3,
        solved_count=0,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )
    mock_goal_repository._convert.return_value = converted_goal

    # 2.
    result = await goal_service.change_goal_status(1, GoalStatus.ACTIVE)

    # 3.
    assert result.status == GoalStatus.ACTIVE
    mock_goal_repository.update_from_model.assert_not_called()


# -------------------------------------------------------
# update_solved_count
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_update_solved_count_increment(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. solved_count 증가 가능한 GoalModel 설정
    2. update_solved_count 호출
    3. solved_count 증가 검증
    """

    # 1.
    goal_model = MagicMock(spec=GoalModel)
    goal_model.solved_count = 1
    goal_model.goal_count = 3

    mock_goal_repository.get.return_value = goal_model
    mock_goal_repository.update_from_model.return_value = Goal(
        id=1,
        user_id=uuid4(),
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=3,
        solved_count=2,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )

    # 2.
    result = await goal_service.update_solved_count(1, delta_solved_count=1)

    # 3.
    assert result.solved_count == 2
    mock_goal_repository.update_from_model.assert_called_once()


@pytest.mark.asyncio
async def test_update_solved_count_negative_error(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. solved_count == 0
    2. 음수 delta 적용
    3. InvalidGoalValueExeception 발생
    """

    # 1.
    goal_model = MagicMock(spec=GoalModel)
    goal_model.solved_count = 0
    goal_model.goal_count = 3
    mock_goal_repository.get.return_value = goal_model

    # 2. & 3.
    with pytest.raises(InvalidGoalValueExeception):
        await goal_service.update_solved_count(1, delta_solved_count=-1)


@pytest.mark.asyncio
async def test_update_solved_count_exceed_error(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. goal_count 초과 delta 설정
    2. update_solved_count 호출
    3. InvalidGoalValueExeception 발생
    """

    # 1.
    goal_model = MagicMock(spec=GoalModel)
    goal_model.solved_count = 2
    goal_model.goal_count = 3
    mock_goal_repository.get.return_value = goal_model

    # 2. & 3.
    with pytest.raises(InvalidGoalValueExeception):
        await goal_service.update_solved_count(1, delta_solved_count=2)


@pytest.mark.asyncio
async def test_update_solved_count_complete(
    goal_service: GoalService,
    mock_goal_repository: AsyncMock,
):
    """
    1. new_count == goal_count
    2. COMPLETED 상태 + finished_at 설정
    3. 결과 검증
    """

    # 1.
    goal_model = MagicMock(spec=GoalModel)
    goal_model.solved_count = 2
    goal_model.goal_count = 3
    mock_goal_repository.get.return_value = goal_model

    updated_goal = Goal(
        id=1,
        user_id=uuid4(),
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=3,
        solved_count=3,
        status=GoalStatus.COMPLETED,
        finished_at=datetime.now(),
    )
    mock_goal_repository.update_from_model.return_value = updated_goal

    # 2.
    result = await goal_service.update_solved_count(1, delta_solved_count=1)

    # 3.
    assert result.status == GoalStatus.COMPLETED
    assert result.solved_count == 3
    assert result.finished_at is not None
