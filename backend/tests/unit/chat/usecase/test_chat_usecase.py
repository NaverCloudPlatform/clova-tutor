# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from chats.domain.chat import Chat, ChatDetail
from chats.presentation.schemas.request_dto import ChatCreateRequestBody, ChatTitleUpdateRequestBody
from chats.presentation.schemas.response_dto import ChatDetailResponse, ChatResponse
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import ChatAccessForbiddenException, ChatNotFoundException
from chats.usecase.chat_usecase import ChatUseCase
from common.presentation.pagination import CursorPaginateParams, CursorPaginateResponse
from goals.domain.goal import Goal, GoalStatus
from goals.service.exceptions import NotFoundGoalException
from goals.service.goal_service import GoalService
from problems.domain.problem import GradeEnum, SubjectEnum


@pytest.fixture
def mock_chat_service() -> AsyncMock:
    return AsyncMock(spec=ChatService)


@pytest.fixture
def mock_chat_problem_service() -> AsyncMock:
    return AsyncMock(spec=ChatProblemService)


@pytest.fixture
def mock_goal_service() -> AsyncMock:
    return AsyncMock(spec=GoalService)


@pytest.fixture
def chat_use_case(
    mock_chat_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
    mock_goal_service: AsyncMock,
) -> ChatUseCase:
    return ChatUseCase(
        chat_service=mock_chat_service,
        chat_problem_service=mock_chat_problem_service,
        goal_service=mock_goal_service,
    )


# =======================================================
# create_chat
# =======================================================

@pytest.mark.asyncio
async def test_create_chat_success(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
):
    """
    1. 채팅 생성 요청 및 반환 Chat 준비
    2. create_chat 호출
    3. 응답 DTO 필드 및 기본 상태 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 1
    TEST_TITLE = "MY CHAT"
    TEST_NOW = datetime.now()

    TEST_CHAT = Chat(
        id=TEST_CHAT_ID,
        title=TEST_TITLE,
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=TEST_NOW,
    )

    mock_chat_service.create_chat.return_value = TEST_CHAT

    TEST_REQUEST = ChatCreateRequestBody(
        title=TEST_TITLE,
        subject="math",
        grade="10",
    )

    # 2.
    response = await chat_use_case.create_chat(
        req=TEST_REQUEST,
        user_id=TEST_USER_ID,
    )

    # 3.
    assert isinstance(response, ChatResponse)
    assert response.id == TEST_CHAT_ID
    assert response.title == TEST_TITLE
    assert response.has_problem is False
    assert response.has_active_goal is False

    mock_chat_service.create_chat.assert_called_once()


# =======================================================
# update_title
# =======================================================

@pytest.mark.asyncio
async def test_update_title_success(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
    mock_goal_service: AsyncMock,
):
    """
    1. 기존 채팅 및 업데이트 결과 조건 준비
    2. update_title 호출
    3. 제목 변경 및 상태 플래그 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 10
    TEST_NEW_TITLE = "NEW TITLE"

    TEST_EXISTING_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="OLD",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.ENGLISH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_EXISTING_CHAT

    TEST_UPDATED_CHAT = Chat(
        id=TEST_CHAT_ID,
        title=TEST_NEW_TITLE,
        user_id=TEST_USER_ID,
        subject=TEST_EXISTING_CHAT.subject,
        grade=TEST_EXISTING_CHAT.grade,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.update_chat_title.return_value = TEST_UPDATED_CHAT

    mock_chat_problem_service.exists_by_chat_id.return_value = True
    mock_goal_service.exists_by_chat_id.return_value = True

    TEST_REQUEST = ChatTitleUpdateRequestBody(title=TEST_NEW_TITLE)

    # 2.
    response = await chat_use_case.update_title(
        chat_id=TEST_CHAT_ID,
        req=TEST_REQUEST,
        user_id=TEST_USER_ID,
    )

    # 3.
    assert isinstance(response, ChatResponse)
    assert response.title == TEST_NEW_TITLE
    assert response.has_problem is True
    assert response.has_active_goal is True

    mock_chat_service.update_chat_title.assert_called_once_with(
        TEST_CHAT_ID,
        TEST_NEW_TITLE,
    )


@pytest.mark.asyncio
async def test_update_title_wrong_user(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
):
    """
    1. 다른 사용자 소유의 채팅 조건 준비
    2. update_title 호출
    3. ChatAccessForbiddenException 발생 검증
    """
    # 1.
    TEST_CHAT_ID = 10
    TEST_MY_USER_ID = uuid.uuid4()
    TEST_OTHER_USER_ID = uuid.uuid4()

    TEST_OTHER_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="X",
        user_id=TEST_OTHER_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_OTHER_CHAT

    TEST_REQUEST = ChatTitleUpdateRequestBody(title="UPDATE")

    # 2. & 3.
    with pytest.raises(ChatAccessForbiddenException):
        await chat_use_case.update_title(
            chat_id=TEST_CHAT_ID,
            req=TEST_REQUEST,
            user_id=TEST_MY_USER_ID,
        )


# =======================================================
# get_chat_detail
# =======================================================

@pytest.mark.asyncio
async def test_get_chat_detail_with_active_goal(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
    mock_goal_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 활성 목표가 존재하는 채팅 조건 준비
    2. get_chat_detail 호출
    3. 활성 목표 및 문제 존재 상태 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 100

    TEST_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="DETAIL",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_CHAT

    TEST_GOAL = Goal(
        id=1,
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        subject=TEST_CHAT.subject,
        goal_count=20,
        solved_count=3,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )
    mock_goal_service.get_goal_by_chat_id.return_value = TEST_GOAL

    mock_chat_problem_service.exists_by_chat_id.return_value = True

    # 2.
    response = await chat_use_case.get_chat_detail(
        chat_id=TEST_CHAT_ID,
        user_id=TEST_USER_ID,
    )

    # 3.
    assert isinstance(response, ChatDetailResponse)
    assert response.has_active_goal is True
    assert response.active_goal.id == 1
    assert response.has_problem is True


@pytest.mark.asyncio
async def test_get_chat_detail_without_active_goal(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
    mock_goal_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 활성 목표가 없는 채팅 조건 준비
    2. get_chat_detail 호출
    3. 목표 및 문제 미존재 상태 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 100

    TEST_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="DETAIL",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_CHAT

    mock_goal_service.get_goal_by_chat_id.side_effect = NotFoundGoalException
    mock_chat_problem_service.exists_by_chat_id.return_value = False

    # 2.
    response = await chat_use_case.get_chat_detail(
        chat_id=TEST_CHAT_ID,
        user_id=TEST_USER_ID,
    )

    # 3.
    assert response.has_active_goal is False
    assert response.active_goal is None
    assert response.has_problem is False


# =======================================================
# get_chat_list
# =======================================================

@pytest.mark.asyncio
async def test_get_chat_list_basic(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
):
    """
    1. 채팅 목록 데이터 조건 준비
    2. get_chat_list 호출
    3. 아이템 개수 및 next_cursor 생성 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_NOW = datetime.now()

    TEST_CHAT_ITEMS = [
        ChatDetail(
            id=i + 1,
            title=f"CHAT-{i}",
            user_id=TEST_USER_ID,
            subject=SubjectEnum.MATH,
            grade=GradeEnum.HIGH_FIRST,
            latest_used_at=TEST_NOW - timedelta(minutes=i),
            has_problem=False,
            has_active_goal=False,
        )
        for i in range(3)
    ]

    mock_chat_service.get_chat_list.return_value = TEST_CHAT_ITEMS

    TEST_PAGINATE = CursorPaginateParams(cursor=None, size=3)

    # 2.
    response = await chat_use_case.get_chat_list(
        user_id=TEST_USER_ID,
        subject=None,
        paginate_filter=TEST_PAGINATE,
    )

    # 3.
    assert isinstance(response, CursorPaginateResponse)
    assert len(response.items) == 3
    assert response.next_cursor is not None

    mock_chat_service.get_chat_list.assert_called_once()


# =======================================================
# delete_chat
# =======================================================

@pytest.mark.asyncio
async def test_delete_chat_success(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 삭제 가능한 채팅 조건 준비
    2. delete_chat 호출
    3. 채팅 및 문제 삭제 호출 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 500

    TEST_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="HELLO",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_CHAT

    # 2.
    await chat_use_case.delete_chat(
        chat_id=TEST_CHAT_ID,
        user_id=TEST_USER_ID,
    )

    # 3.
    mock_chat_service.delete_chat.assert_called_once_with(TEST_CHAT_ID)
    mock_chat_problem_service.delete_chat_problems_by_chat_id.assert_called_once_with(
        chat_id=TEST_CHAT_ID,
    )


@pytest.mark.asyncio
async def test_delete_chat_wrong_user(
    chat_use_case: ChatUseCase,
    mock_chat_service: AsyncMock,
):
    """
    1. 다른 사용자 소유의 채팅 조건 준비
    2. delete_chat 호출
    3. ChatAccessForbiddenException 발생 검증
    """
    # 1.
    TEST_MY_USER_ID = uuid.uuid4()
    TEST_OTHER_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 800

    TEST_OTHER_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="X",
        user_id=TEST_OTHER_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_OTHER_CHAT

    # 2. & 3.
    with pytest.raises(ChatAccessForbiddenException):
        await chat_use_case.delete_chat(
            chat_id=TEST_CHAT_ID,
            user_id=TEST_MY_USER_ID,
        )
