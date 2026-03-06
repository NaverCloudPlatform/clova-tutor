# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from chats.database.models import ChatModel
from chats.database.repository.chat_repository import ChatFilter, ChatRepository
from chats.domain.chat import Chat, ChatDetail
from chats.service.chat_service import ChatService
from chats.service.exceptions import ChatNotFoundException
from problems.domain.problem import GradeEnum, SubjectEnum


@pytest.fixture
def mock_chat_repository() -> AsyncMock:
    return AsyncMock(spec=ChatRepository)

@pytest.fixture
def chat_service(mock_chat_repository: AsyncMock) -> ChatService:
    return ChatService(chat_repo=mock_chat_repository)


# -------------------------------------------------------
# get_chat_by_id
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_chat_by_id_success(chat_service, mock_chat_repository):
    """
    1. ChatRepository.get 이 Chat 을 반환하도록 조건 준비
    2. get_chat_by_id 호출
    3. Chat 객체 반환 및 repository 호출 인자 검증
    """
    # 1.
    TEST_CHAT = Chat(
        id=1,
        title="test",
        user_id=uuid4(),
        grade=GradeEnum.ELEMENTARY_FIRST,
        subject=SubjectEnum.MATH,
        latest_used_at=datetime.now()
    )
    mock_chat_repository.get.return_value = TEST_CHAT

    # 2.
    result = await chat_service.get_chat_by_id(1)

    # 3.
    assert isinstance(result, Chat)
    mock_chat_repository.get.assert_called_once()
    _, kwargs = mock_chat_repository.get.call_args
    assert kwargs["flt"].id == 1


@pytest.mark.asyncio
async def test_get_chat_by_id_not_found(chat_service, mock_chat_repository):
    """
    1. ChatRepository.get 이 None 을 반환하도록 조건 준비
    2. get_chat_by_id 호출
    3. ChatNotFoundException 발생 확인
    """

    # 1.
    mock_chat_repository.get.return_value = None

    # 2. & 3.
    with pytest.raises(ChatNotFoundException):
        await chat_service.get_chat_by_id(999)


# -------------------------------------------------------
# get_chat_list
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_chat_list_basic(chat_service, mock_chat_repository):
    """
    1. ChatRepository.get_chat_list 이 ChatDetail 리스트를 반환하도록 준비
    2. get_chat_list 호출
    3. 반환값 및 ChatFilter 전달 여부 확인
    """

    # 1.
    TEST_CHATS = [
        ChatDetail(
            id=1,
            title="test",
            user_id=uuid4(),
            subject=SubjectEnum.MATH,
            grade=GradeEnum.ELEMENTARY_FIRST,
            latest_used_at=datetime.now(),
            has_problem=False,
            has_active_goal=False
        )
    ]
    mock_chat_repository.get_chat_list.return_value = TEST_CHATS

    # 2.
    result = await chat_service.get_chat_list(user_id=uuid4())

    # 3.
    assert result == TEST_CHATS
    mock_chat_repository.get_chat_list.assert_called_once()
    _, kwargs = mock_chat_repository.get_chat_list.call_args
    assert isinstance(kwargs["flt"], ChatFilter)


@pytest.mark.asyncio
async def test_get_chat_list_with_subject_filter(chat_service, mock_chat_repository):
    """
    1. subject 필터가 포함된 ChatDetail 리스트 반환 조건 준비
    2. subject_list 인자를 포함해 get_chat_list 호출
    3. ChatFilter.subject 에 값이 전달되었는지 확인
    """

    # 1.
    TEST_CHATS = [
        ChatDetail(
            id=2,
            title="math-chat",
            user_id=uuid4(),
            subject=SubjectEnum.MATH,
            grade=GradeEnum.ELEMENTARY_FIRST,
            latest_used_at=datetime.now(),
            has_problem=False,
            has_active_goal=False
        )
    ]
    mock_chat_repository.get_chat_list.return_value = TEST_CHATS

    # 2.
    result = await chat_service.get_chat_list(
        user_id=uuid4(),
        subject_list=[SubjectEnum.MATH]
    )

    # 3.
    assert result == TEST_CHATS
    _, kwargs = mock_chat_repository.get_chat_list.call_args
    assert kwargs["flt"].subject == [SubjectEnum.MATH]


# -------------------------------------------------------
# update_chat_latest_used_at
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_update_chat_latest_used_at_success(chat_service, mock_chat_repository):
    """
    1. ChatRepository.update 가 1 을 반환하도록 조건 준비
    2. update_chat_latest_used_at 호출
    3. True 반환 확인
    """

    # 1.
    mock_chat_repository.update.return_value = 1

    # 2.
    result = await chat_service.update_chat_latest_used_at(chat_id=5)

    # 3.
    assert result is True
    mock_chat_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_chat_latest_used_at_fail(chat_service, mock_chat_repository):
    """
    1. ChatRepository.update 가 0 을 반환하도록 조건 준비
    2. update_chat_latest_used_at 호출
    3. False 반환 확인
    """

    # 1.
    mock_chat_repository.update.return_value = 0

    # 2.
    result = await chat_service.update_chat_latest_used_at(chat_id=5)

    # 3.
    assert result is False


# -------------------------------------------------------
# create_chat
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_create_chat_success(chat_service, mock_chat_repository):
    """
    1. ChatRepository.create 가 Chat 을 반환하도록 조건 준비
    2. create_chat 호출
    3. 생성된 Chat 반환 및 생성 인자 검증
    """

    # 1.
    TEST_USER = uuid4()
    now = datetime.now()

    TEST_CHAT = Chat(
        id=10,
        title="hello",
        user_id=TEST_USER,
        grade=GradeEnum.ELEMENTARY_FIRST,
        subject=SubjectEnum.MATH,
        latest_used_at=now
    )

    mock_chat_repository.create.return_value =TEST_CHAT

    # 2.
    result = await chat_service.create_chat(
        title="hello",
        user_id=TEST_USER,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.ELEMENTARY_FIRST
    )

    # 3.
    assert result.id == 10
    mock_chat_repository.create.assert_called_once()
    created_arg = mock_chat_repository.create.call_args.args[0]
    assert created_arg.title == "hello"
    assert created_arg.user_id == TEST_USER
    assert created_arg.subject == SubjectEnum.MATH


# -------------------------------------------------------
# update_chat_title
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_update_chat_title_success(chat_service, mock_chat_repository):
    """
    1. 기존 ChatModel 이 존재하도록 조건 준비
    2. update_chat_title 호출
    3. 변경된 title 이 반영된 Chat 반환 확인
    """

    # 1.
    mock_chat_repository.get.return_value = ChatModel(id=5)
    mock_chat_repository.update_from_model.return_value = Chat(
        id=5,
        title="new title",
        user_id=uuid4(),
        grade=GradeEnum.ELEMENTARY_FIRST,
        subject=SubjectEnum.ENGLISH,
        latest_used_at=datetime.now()
    )

    # 2.
    result = await chat_service.update_chat_title(chat_id=5, title="new title")

    # 3.
    assert result.title == "new title"
    mock_chat_repository.get.assert_called_once()
    mock_chat_repository.update_from_model.assert_called_once()


@pytest.mark.asyncio
async def test_update_chat_title_not_found(chat_service, mock_chat_repository):
    """
    1. ChatRepository.get 이 None 을 반환하도록 조건 준비
    2. update_chat_title 호출
    3. ChatNotFoundException 발생 확인
    """

    # 1.
    mock_chat_repository.get.return_value = None

    # 2. & 3.
    with pytest.raises(ChatNotFoundException):
        await chat_service.update_chat_title(chat_id=999, title="x")


# -------------------------------------------------------
# delete_chat
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_chat(chat_service, mock_chat_repository):
    """
    1. 삭제 대상 chat_id 조건 준비
    2. delete_chat 호출
    3. ChatRepository.delete 가 올바른 필터로 호출되었는지 확인
    """

    # 1.
    chat_id = 10

    # 2.
    await chat_service.delete_chat(chat_id=chat_id)

    # 3.
    mock_chat_repository.delete.assert_called_once()
    _, kwargs = mock_chat_repository.delete.call_args
    assert kwargs["flt"].id == chat_id
