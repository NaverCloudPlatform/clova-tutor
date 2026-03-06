# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from chats.database.models import ChatMessageModel
from chats.domain.chat_message.chat_message import (
    ChatMessage,
    ChatMessageWithDate,
    MessageRole,
    MessageType,
)
from chats.domain.chat_message.metadata import ChatMessageMetadata
from chats.domain.chat_message.system_content import (
    DateValue,
    SystemMessageContent,
    SystemMessageSubType,
)
from chats.service.chat_message_service import ChatMessageService
from chats.service.chat_service import ChatService


@pytest.fixture
def mock_chat_repo():
    return AsyncMock()


@pytest.fixture
def mock_chat_message_repo():
    m = AsyncMock()
    m._convert = MagicMock()
    return m


@pytest.fixture
def chat_message_service(
    mock_chat_repo,
    mock_chat_message_repo,
):
    chat_service = ChatService(chat_repo=mock_chat_repo)
    return ChatMessageService(
        chat_service=chat_service,
        chat_message_repo=mock_chat_message_repo,
    )


# =======================================================
# exists_by_chat_id
# =======================================================

@pytest.mark.asyncio
async def test_exists_by_chat_id(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. 특정 chat_id + role 조건에 대해 메시지가 존재하도록 설정
    2. exists_by_chat_id 호출
    3. True 반환 및 exists 호출 확인
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_ROLE = [MessageRole.USER]
    mock_chat_message_repo.exists.return_value = True

    # 2.
    result = await chat_message_service.exists_by_chat_id(
        chat_id=TEST_CHAT_ID,
        role=TEST_ROLE,
    )

    # 3.
    assert result is True
    mock_chat_message_repo.exists.assert_called_once()


@pytest.mark.asyncio
async def test_exists_by_chat_id_empty_role(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. role 이 빈 리스트인 조건에서 메시지가 없도록 설정
    2. exists_by_chat_id 호출
    3. False 반환 및 filter.role 값 검증
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_ROLE = []
    mock_chat_message_repo.exists.return_value = False

    # 2.
    result = await chat_message_service.exists_by_chat_id(
        chat_id=TEST_CHAT_ID,
        role=TEST_ROLE,
    )

    # 3.
    assert result is False
    mock_chat_message_repo.exists.assert_called_once()

    _, kwargs = mock_chat_message_repo.exists.call_args
    flt = kwargs["flt"]
    assert flt.role == TEST_ROLE

# =======================================================
# get_chat_messages
# =======================================================

@pytest.mark.asyncio
async def test_get_chat_messages(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. 단일 ChatMessageModel 목록 준비
    2. get_chat_messages 호출
    3. ChatMessageWithDate 리스트 반환 확인
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_CREATED_AT = datetime.now()

    TEST_MODEL = ChatMessageModel(
        id=1,
        chat_id=TEST_CHAT_ID,
        role=MessageRole.USER,
        type=MessageType.CHAT,
        content=[],
        meta_data={},
        created_at=TEST_CREATED_AT,
    )

    mock_chat_message_repo.get_list.return_value = [TEST_MODEL]

    TEST_DOMAIN = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.CHAT,
        role=MessageRole.USER,
        content=[],
        meta_data=ChatMessageMetadata(),
    )
    mock_chat_message_repo._convert.return_value = TEST_DOMAIN

    # 2.
    msgs = await chat_message_service.get_chat_messages(TEST_CHAT_ID)

    # 3.
    assert len(msgs) == 1
    assert isinstance(msgs[0], ChatMessageWithDate)
    mock_chat_message_repo.get_list.assert_called_once()


@pytest.mark.asyncio
async def test_get_chat_messages_convert_call_count(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. 여러 개의 ChatMessageModel 목록 준비
    2. get_chat_messages 호출
    3. convert 가 모델 개수만큼 호출되는지 검증
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_MODELS = [
        ChatMessageModel(
            id=i,
            chat_id=TEST_CHAT_ID,
            role=MessageRole.USER,
            type=MessageType.CHAT,
            content=[],
            meta_data={},
            created_at=datetime.now(),
        )
        for i in range(3)
    ]

    mock_chat_message_repo.get_list.return_value = TEST_MODELS
    mock_chat_message_repo._convert.return_value = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.CHAT,
        role=MessageRole.USER,
        content=[],
        meta_data=ChatMessageMetadata(),
    )

    # 2.
    msgs = await chat_message_service.get_chat_messages(TEST_CHAT_ID)

    # 3.
    assert len(msgs) == 3
    assert mock_chat_message_repo._convert.call_count == 3

# =======================================================
# get_latest_message
# =======================================================

@pytest.mark.asyncio
async def test_get_latest_message(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. 최신 메시지 1개가 반환되도록 repository 설정
    2. get_latest_message 호출
    3. ChatMessageWithDate 반환 확인
    """
    # 1.
    TEST_CHAT_ID = 1

    TEST_MODEL = ChatMessageModel(
        id=1,
        chat_id=TEST_CHAT_ID,
        role=MessageRole.USER,
        type=MessageType.CHAT,
        content=[],
        meta_data={},
        created_at=datetime.now(),
    )
    mock_chat_message_repo.get_list.return_value = [TEST_MODEL]

    mock_chat_message_repo._convert.return_value = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.CHAT,
        role=MessageRole.USER,
        content=[],
        meta_data=ChatMessageMetadata(),
    )

    # 2.
    msg = await chat_message_service.get_latest_message(TEST_CHAT_ID)

    # 3.
    assert msg is not None
    assert isinstance(msg, ChatMessageWithDate)


@pytest.mark.asyncio
async def test_get_latest_message_filter_arguments(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. 메시지가 없는 상태 준비
    2. get_latest_message 호출
    3. size=1 및 order_by 전달 여부 확인
    """
    # 1.
    TEST_CHAT_ID = 1
    mock_chat_message_repo.get_list.return_value = []

    # 2.
    await chat_message_service.get_latest_message(TEST_CHAT_ID)

    # 3.
    mock_chat_message_repo.get_list.assert_called_once()
    _, kwargs = mock_chat_message_repo.get_list.call_args

    assert kwargs["size"] == 1
    assert "order_by" in kwargs
    assert len(kwargs["order_by"]) == 1

# =======================================================
# create_system_message
# =======================================================

@pytest.mark.asyncio
async def test_create_system_message(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. 시스템 메시지 생성 결과 준비
    2. create_system_message 호출
    3. role/type 및 create 호출 확인
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_CONTENTS = [
        SystemMessageContent(
            value=DateValue(text="hi"),
            m_type=SystemMessageSubType.DATE,
        )
    ]

    mock_chat_message_repo.create.return_value = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.SYSTEM,
        role=MessageRole.SYSTEM,
        content=TEST_CONTENTS,
        meta_data=ChatMessageMetadata(),
    )

    # 2.
    result = await chat_message_service.create_system_message(
        chat_id=TEST_CHAT_ID,
        contents=TEST_CONTENTS,
    )

    # 3.
    assert result.role == MessageRole.SYSTEM
    assert result.type == MessageType.SYSTEM
    mock_chat_message_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_system_message_fields(
    chat_message_service,
    mock_chat_message_repo,
):
    """
    1. 시스템 메시지 content 준비
    2. create_system_message 호출
    3. create 에 전달된 ChatMessage 필드 검증
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_CONTENT = SystemMessageContent(
        value=DateValue(text="hi"),
        m_type=SystemMessageSubType.DATE,
    )

    mock_chat_message_repo.create.return_value = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.SYSTEM,
        role=MessageRole.SYSTEM,
        content=[TEST_CONTENT],
        meta_data=ChatMessageMetadata(),
    )

    # 2.
    await chat_message_service.create_system_message(
        chat_id=TEST_CHAT_ID,
        contents=[TEST_CONTENT],
    )

    # 3.
    args, _ = mock_chat_message_repo.create.call_args
    passed_msg = args[0]

    assert passed_msg.chat_id == TEST_CHAT_ID
    assert passed_msg.role == MessageRole.SYSTEM
    assert passed_msg.type == MessageType.SYSTEM

# =======================================================
# create_user_message
# =======================================================

@pytest.mark.asyncio
async def test_create_user_message(
    chat_message_service,
    mock_chat_message_repo,
    mock_chat_repo,
):
    """
    1. 사용자 메시지 모델 및 convert 결과 준비
    2. create_user_message 호출
    3. USER role 반환 및 chat update 호출 확인
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_CREATED_AT = datetime.now()

    TEST_MODEL = ChatMessageModel(
        id=1,
        chat_id=TEST_CHAT_ID,
        role=MessageRole.USER,
        type=MessageType.CHAT,
        content=[],
        meta_data={},
        created_at=TEST_CREATED_AT,
    )

    mock_chat_message_repo.create.return_value = TEST_MODEL
    mock_chat_message_repo._convert.return_value = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.CHAT,
        role=MessageRole.USER,
        content=[],
        meta_data=ChatMessageMetadata(),
    )
    mock_chat_repo.update.return_value = 1

    # 2.
    result = await chat_message_service.create_user_message(
        chat_id=TEST_CHAT_ID,
        contents=[],
        metadata=ChatMessageMetadata(),
    )

    # 3.
    assert result.role == MessageRole.USER
    mock_chat_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_message_update_called_after_create(
    chat_message_service,
    mock_chat_message_repo,
    mock_chat_repo,
):
    """
    1. 사용자 메시지 생성 상황 준비
    2. create_user_message 호출
    3. create 이후 update 가 호출되었는지 확인
    """
    # 1.
    TEST_CHAT_ID = 5
    TEST_CREATED_AT = datetime.now()

    TEST_MODEL = ChatMessageModel(
        id=1,
        chat_id=TEST_CHAT_ID,
        created_at=TEST_CREATED_AT,
        role=MessageRole.USER,
        type=MessageType.CHAT,
        content=[],
        meta_data={},
    )

    mock_chat_message_repo.create.return_value = TEST_MODEL
    mock_chat_message_repo._convert.return_value = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.CHAT,
        role=MessageRole.USER,
        content=[],
        meta_data=ChatMessageMetadata(),
    )
    mock_chat_repo.update.return_value = 1

    # 2.
    await chat_message_service.create_user_message(
        chat_id=TEST_CHAT_ID,
        contents=[],
        metadata=ChatMessageMetadata(),
    )

    # 3.
    assert mock_chat_message_repo.create.call_count == 1
    assert mock_chat_repo.update.call_count == 1

# =======================================================
# create_assistant_message
# =======================================================

@pytest.mark.asyncio
async def test_create_assistant_message(
    chat_message_service,
    mock_chat_message_repo,
    mock_chat_repo,
):
    """
    1. 어시스턴트 메시지 생성 상황 준비
    2. create_assistant_message 호출
    3. ASSISTANT role 반환 및 chat update 호출 확인
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_CREATED_AT = datetime.now()

    TEST_MODEL = ChatMessageModel(
        id=1,
        chat_id=TEST_CHAT_ID,
        role=MessageRole.ASSISTANT,
        type=MessageType.CHAT,
        content=[],
        meta_data={},
        created_at=TEST_CREATED_AT,
    )

    mock_chat_message_repo.create.return_value = TEST_MODEL
    mock_chat_message_repo._convert.return_value = ChatMessage(
        chat_id=TEST_CHAT_ID,
        type=MessageType.CHAT,
        role=MessageRole.ASSISTANT,
        content=[],
        meta_data=ChatMessageMetadata(),
    )
    mock_chat_repo.update.return_value = 1

    # 2.
    result = await chat_message_service.create_assistant_message(
        chat_id=TEST_CHAT_ID,
        contents=[],
        metadata=ChatMessageMetadata(),
    )

    # 3.
    assert result.role == MessageRole.ASSISTANT
    mock_chat_repo.update.assert_called_once()
