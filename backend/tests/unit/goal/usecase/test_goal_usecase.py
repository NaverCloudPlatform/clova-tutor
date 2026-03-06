# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from chats.domain.chat import Chat
from chats.service.chat_service import ChatService
from goals.domain.goal import Goal, GoalStatus
from goals.presentation.schemas.request_dto import GoalCreateRequestBody
from goals.presentation.schemas.response_dto import GoalResponse
from goals.service.exceptions import NotFoundGoalException
from goals.service.goal_service import GoalService
from goals.usecase.exceptions import ActiveGoalExistException
from goals.usecase.goal_usecase import GoalUseCase
from problems.domain.problem import GradeEnum, SubjectEnum


@pytest.fixture
def mock_chat_service() -> AsyncMock:
    return AsyncMock(spec=ChatService)


@pytest.fixture
def mock_goal_service() -> AsyncMock:
    return AsyncMock(spec=GoalService)


@pytest.fixture
def goal_use_case(
    mock_chat_service: AsyncMock,
    mock_goal_service: AsyncMock,
) -> GoalUseCase:
    return GoalUseCase(
        chat_service=mock_chat_service,
        goal_service=mock_goal_service,
    )


# -------------------------------------------------------
# create_active_goal : success
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_active_goal_success(
    goal_use_case: GoalUseCase,
    mock_chat_service: AsyncMock,
    mock_goal_service: AsyncMock,
):
    """
    1. chat 존재 + ACTIVE goal 없음
    2. create_active_goal 호출
    3. GoalResponse 반환 및 service 호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 100
    TEST_GOAL_COUNT = 20
    TEST_SUBJECT = SubjectEnum.MATH

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="test chat",
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    mock_goal_service.get_goal_by_chat_id.side_effect = NotFoundGoalException

    created_goal = Goal(
        id=1,
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        subject=TEST_SUBJECT,
        goal_count=TEST_GOAL_COUNT,
        solved_count=0,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )
    mock_goal_service.create_goal.return_value = created_goal

    request = GoalCreateRequestBody(
        chat_id=TEST_CHAT_ID,
        goal_count=TEST_GOAL_COUNT,
    )

    # 2.
    response = await goal_use_case.create_active_goal(
        user_id=TEST_USER_ID,
        requset=request,
    )

    # 3.
    assert isinstance(response, GoalResponse)
    assert response.id == 1
    assert response.goal_count == TEST_GOAL_COUNT
    assert response.solved_count == 0

    mock_chat_service.get_chat_by_id.assert_called_once_with(
        chat_id=TEST_CHAT_ID
    )
    mock_goal_service.get_goal_by_chat_id.assert_called_once_with(
        TEST_CHAT_ID,
        status=GoalStatus.ACTIVE,
    )
    mock_goal_service.create_goal.assert_called_once_with(
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        subject=TEST_SUBJECT,
        goal_count=TEST_GOAL_COUNT,
    )


# -------------------------------------------------------
# create_active_goal : already exists
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_active_goal_existing_active(
    goal_use_case: GoalUseCase,
    mock_chat_service: AsyncMock,
    mock_goal_service: AsyncMock,
):
    """
    1. chat 존재 + ACTIVE goal 존재
    2. create_active_goal 호출
    3. ActiveGoalExistException 발생
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 99999
    TEST_SUBJECT = SubjectEnum.MATH

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="existing chat",
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    mock_goal_service.get_goal_by_chat_id.return_value = Goal(
        id=1,
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        subject=TEST_SUBJECT,
        goal_count=10,
        solved_count=3,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )

    request = GoalCreateRequestBody(
        chat_id=TEST_CHAT_ID,
        goal_count=10,
    )

    # 2. & 3.
    with pytest.raises(ActiveGoalExistException):
        await goal_use_case.create_active_goal(
            user_id=TEST_USER_ID,
            requset=request,
        )

    mock_chat_service.get_chat_by_id.assert_called_once()
    mock_goal_service.get_goal_by_chat_id.assert_called_once()
    mock_goal_service.create_goal.assert_not_called()


# -------------------------------------------------------
# cancel_goal
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_goal_success(
    goal_use_case: GoalUseCase,
    mock_goal_service: AsyncMock,
):
    """
    1. goal 조회 → user_id 일치
    2. cancel_goal 호출
    3. CANCELLED 상태 변경 요청 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_GOAL_ID = 10

    mock_goal_service.get_goal_by_id.return_value = Goal(
        id=TEST_GOAL_ID,
        user_id=TEST_USER_ID,
        chat_id=1,
        subject=SubjectEnum.MATH,
        goal_count=20,
        solved_count=5,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )

    # 2.
    await goal_use_case.cancel_goal(
        user_id=TEST_USER_ID,
        goal_id=TEST_GOAL_ID,
    )

    # 3.
    mock_goal_service.get_goal_by_id.assert_called_once_with(
        TEST_GOAL_ID
    )
    mock_goal_service.change_goal_status.assert_called_once_with(
        TEST_GOAL_ID,
        GoalStatus.CANCELLED,
    )


# -------------------------------------------------------
# cancel_goal
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_goal_wrong_user(
    goal_use_case: GoalUseCase,
    mock_goal_service: AsyncMock,
):
    """
    1. goal 조회 → user_id 불일치
    2. cancel_goal 호출
    3. NotFoundGoalException 발생
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    OTHER_USER_ID = uuid.uuid4()
    TEST_GOAL_ID = 10

    mock_goal_service.get_goal_by_id.return_value = Goal(
        id=TEST_GOAL_ID,
        user_id=OTHER_USER_ID,
        chat_id=1,
        subject=SubjectEnum.ENGLISH,
        goal_count=5,
        solved_count=1,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )

    # 2. & 3.
    with pytest.raises(NotFoundGoalException):
        await goal_use_case.cancel_goal(
            user_id=TEST_USER_ID,
            goal_id=TEST_GOAL_ID,
        )

    mock_goal_service.change_goal_status.assert_not_called()
