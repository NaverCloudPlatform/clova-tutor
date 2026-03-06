# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
import uuid

from contextlib import asynccontextmanager
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from chats.domain.chat import Chat
from chats.domain.chat_message.chat_message import ChatStreamStatus, MessageRole
from chats.domain.chat_message.message_content import create_text_content
from chats.domain.chat_message.metadata import (
    ChatMessageMetadata,
    ReActModelToolType,
    SystemHint,
    ToolInfo,
)
from chats.presentation.schemas.response_dto import ChatMessageResponse, StopResponseStatusValue
from chats.service.chat_message_service import ChatMessageService
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import (
    ChatAccessForbiddenException,
    ChatNotFoundException,
)
from chats.service.i_assistant_service import IAssistantService
from chats.service.i_stream_lock_service import IStreamLockService
from chats.service.i_stream_service import IChatStreamService
from chats.usecase.chat_message_usecase import (
    ChatMessageUseCase,
    ProblemRecommendStatus,
)
from problems.domain.problem import GradeEnum, SubjectEnum
from tests.fakes import DEFAULT_CHUNKS, PROBLEM_CHUNKS, async_chunk_generator


@pytest.fixture
def mock_chat_service():
    return AsyncMock(spec=ChatService)

@pytest.fixture
def mock_chat_message_service():
    return AsyncMock(spec=ChatMessageService)

@pytest.fixture
def mock_chat_problem_service():
    return AsyncMock(spec=ChatProblemService)

@pytest.fixture
def mock_stream_lock_service():
    return AsyncMock(spec=IStreamLockService)

@pytest.fixture
def mock_assistant_service():
    return AsyncMock(spec=IAssistantService)

@pytest.fixture
def mock_chat_stream_service():
    return AsyncMock(spec=IChatStreamService)

@pytest.fixture
def chat_message_use_case(
    mock_chat_service,
    mock_chat_message_service,
    mock_chat_problem_service,
    mock_stream_lock_service,
    mock_assistant_service,
    mock_chat_stream_service,
):
    return ChatMessageUseCase(
        chat_service=mock_chat_service,
        chat_message_service=mock_chat_message_service,
        chat_problem_service=mock_chat_problem_service,
        stream_lock_service=mock_stream_lock_service,
        assistant_service=mock_assistant_service,
        chat_stream_service=mock_chat_stream_service,
    )


# =========================================================
# _validate_chat
# =========================================================

@pytest.mark.asyncio
async def test_validate_chat_success(
    chat_message_use_case,
    mock_chat_service,
):
    """
    1. 본인 소유 Chat 이 존재한다
    2. _validate_chat 호출
    3. Chat 객체를 반환한다
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 1

    TEST_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="test",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_CHAT

    # 2.
    RESULT = await chat_message_use_case._validate_chat(
        chat_id=TEST_CHAT_ID,
        user_id=TEST_USER_ID,
    )

    # 3.
    assert RESULT == TEST_CHAT
    mock_chat_service.get_chat_by_id.assert_called_once_with(TEST_CHAT_ID)


@pytest.mark.asyncio
async def test_validate_chat_wrong_user(
    chat_message_use_case,
    mock_chat_service,
):
    """
    1. 다른 유저의 Chat 이 존재한다
    2. _validate_chat 호출
    3. ChatAccessForbiddenException 이 발생한다
    """
    # 1.
    TEST_MY_USER_ID = uuid.uuid4()
    TEST_OTHER_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 1

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="x",
        user_id=TEST_OTHER_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    # 2. & 3.
    with pytest.raises(ChatAccessForbiddenException):
        await chat_message_use_case._validate_chat(
            TEST_CHAT_ID,
            TEST_MY_USER_ID,
        )


# =========================================================
# _create_sse_payload
# =========================================================

def test_create_sse_payload_success(chat_message_use_case):
    """
    1. contents 와 metadata 가 주어진다
    2. _create_sse_payload 호출
    3. ChatMessageResponse 가 생성된다
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_CONTENTS = [create_text_content("hello")]
    TEST_METADATA = ChatMessageMetadata(
        tools=[ToolInfo(
            name=ReActModelToolType.DEFAULT_CHAT,
            value={}
        )],
        system_hints=[SystemHint.TRANSLATION_BUTTON],
    )

    # 2.
    RESULT = chat_message_use_case._create_sse_payload(
        chat_id=TEST_CHAT_ID,
        contents=TEST_CONTENTS,
        metadata=TEST_METADATA,
    )

    # 3.
    assert isinstance(RESULT, ChatMessageResponse)
    assert RESULT.chat_id == TEST_CHAT_ID
    assert RESULT.author.role == MessageRole.ASSISTANT
    assert len(RESULT.contents) >= 1


# =========================================================
# _ensure_today_header
# =========================================================

@pytest.mark.asyncio
async def test_ensure_today_header_create(
    chat_message_use_case,
    mock_chat_message_service,
):
    """
    1. 마지막 메시지가 없거나 날짜가 다르다
    2. _ensure_today_header 호출
    3. 날짜 시스템 메시지가 생성된다
    """
    # 1.
    TEST_CHAT_ID = 1

    mock_chat_message_service.get_latest_message.return_value = None

    # 2.
    await chat_message_use_case._ensure_today_header(TEST_CHAT_ID)

    # 3.
    mock_chat_message_service.create_system_message.assert_called_once()


# =========================================================
# _problem_update
# =========================================================

@pytest.mark.asyncio
async def test_problem_update_duplicate_random_success(
    chat_message_use_case,
    mock_chat_problem_service,
):
    """
    1. 추천 문제가 중복이다
    2. _problem_update 호출
    3. RANDOM_PROBLEM_RECOMMENDED 반환
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_USER_ID = uuid.uuid4()

    TEST_STATE = MagicMock()
    TEST_STATE.recommendation.recommended_problem_id = "p1"

    mock_chat_problem_service.exists_by_problem_id.return_value = True

    TEST_PROBLEM = MagicMock()
    TEST_PROBLEM.id = "random1"
    mock_chat_problem_service.find_not_duplicate_problem.return_value = TEST_PROBLEM

    # 2.
    RESULT = await chat_message_use_case._problem_update(
        chat_id=TEST_CHAT_ID,
        user_id=TEST_USER_ID,
        state=TEST_STATE,
    )

    # 3.
    assert RESULT.status == ProblemRecommendStatus.RANDOM_PROBLEM_RECOMMENDED
    assert RESULT.problem_id == "random1"


@pytest.mark.asyncio
async def test_problem_update_new_problem(
    chat_message_use_case,
    mock_chat_problem_service,
):
    """
    1. 추천 문제가 신규이다
    2. _problem_update 호출
    3. PROBLEM_RECOMMENDED 반환
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_USER_ID = uuid.uuid4()
    TEST_PROBLEM_ID = "p100"

    TEST_STATE = MagicMock()
    TEST_STATE.recommendation.recommended_problem_id = TEST_PROBLEM_ID

    mock_chat_problem_service.exists_by_problem_id.return_value = False

    # 2.
    RESULT = await chat_message_use_case._problem_update(
        TEST_CHAT_ID,
        TEST_USER_ID,
        TEST_STATE,
    )

    # 3.
    assert RESULT.status == ProblemRecommendStatus.PROBLEM_RECOMMENDED
    assert RESULT.problem_id == TEST_PROBLEM_ID

# =========================================================
# get_chat_status
# =========================================================

@pytest.mark.asyncio
async def test_get_chat_status_success(
    chat_message_use_case,
    mock_chat_service,
    mock_stream_lock_service,
):
    """
    1. Chat 이 존재한다
    2. get_chat_status 호출
    3. 상태가 반환된다
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_USER_ID = uuid.uuid4()

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="x",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    TEST_STATUS = MagicMock()
    TEST_STATUS.status = ChatStreamStatus.IS_STREAMING
    mock_stream_lock_service.check_status.return_value = TEST_STATUS

    # 2.
    RESULT = await chat_message_use_case.get_chat_status(
        TEST_CHAT_ID,
        TEST_USER_ID,
    )

    # 3.
    assert RESULT.status == ChatStreamStatus.IS_STREAMING


# =========================================================
# stop_stream
# =========================================================

@pytest.mark.asyncio
async def test_stop_stream_success(
    chat_message_use_case,
    mock_chat_service,
    mock_stream_lock_service,
    mock_chat_stream_service,
    mock_chat_message_service,
):
    """
    1. 스트림이 진행 중이다
    2. stop_stream 호출
    3. 정상 종료된다
    """

    # 1.
    TEST_CHAT_ID = 1
    TEST_USER_ID = uuid.uuid4()

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="x",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    TEST_STATUS = MagicMock()
    TEST_STATUS.status = ChatStreamStatus.IS_STREAMING
    TEST_STATUS.stream_id = "stream1"
    mock_stream_lock_service.check_status.return_value = TEST_STATUS

    mock_chat_stream_service.read_all_messages_from_stream.return_value = []

    # 2.
    RESULT = await chat_message_use_case.stop_stream(
        TEST_CHAT_ID,
        TEST_USER_ID,
    )

    # 3.
    assert RESULT.status == StopResponseStatusValue.OK
    mock_stream_lock_service.release_lock.assert_called_once_with(TEST_CHAT_ID)


# =========================================================
# _stream_producer_task
# =========================================================

@pytest.mark.asyncio
async def test_stream_producer_task_success(
    chat_message_use_case,
    mock_assistant_service,
    mock_stream_lock_service,
    mock_chat_stream_service,
):
    """
    1. 모델 응답 스트림과 락 획득 성공 상태를 준비한다
    2. _stream_producer_task 를 실행한다
    3. stream 메시지가 finish 상태로 전송된다
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_USER_ID = uuid.uuid4()
    TEST_REQUEST_ID = uuid.uuid4()

    TEST_REQUEST = MagicMock()
    TEST_REQUEST.request_id = TEST_REQUEST_ID

    TEST_QUEUE = asyncio.Queue()

    @asynccontextmanager
    async def fake_lock(*args, **kwargs):
        yield True

    mock_stream_lock_service.acquire_lock.return_value = fake_lock()
    mock_assistant_service.get_model_stream_response.return_value = async_chunk_generator(DEFAULT_CHUNKS)

    # 2.
    await chat_message_use_case._stream_producer_task(
        req=TEST_REQUEST,
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        chat_stream_channel=TEST_QUEUE,
    )

    # 3.
    mock_chat_stream_service.add_stream_message.assert_called()
    mock_chat_stream_service.delete_stream_message.assert_called()


@pytest.mark.asyncio
async def test_stream_producer_task_problem_recommended(
    chat_message_use_case,
    mock_assistant_service,
    mock_chat_stream_service,
    mock_stream_lock_service,
):
    """
    1. 문제 추천 스트림 응답을 준비한다
    2. _stream_producer_task 를 실행한다
    3. finish 메시지가 전송된다
    """
    # 1.
    TEST_CHAT_ID = 1
    TEST_USER_ID = uuid.uuid4()

    TEST_REQUEST = MagicMock()
    TEST_REQUEST.request_id = uuid.uuid4()

    TEST_QUEUE = asyncio.Queue()

    @asynccontextmanager
    async def fake_lock(*args, **kwargs):
        yield True

    mock_stream_lock_service.acquire_lock.return_value = fake_lock()
    mock_assistant_service.get_model_stream_response.return_value = (
        async_chunk_generator(PROBLEM_CHUNKS)
    )

    # 2.
    await chat_message_use_case._stream_producer_task(
        req=TEST_REQUEST,
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        chat_stream_channel=TEST_QUEUE,
    )

    # 3.
    mock_chat_stream_service.add_stream_message.assert_called()
    mock_chat_stream_service.delete_stream_message.assert_called_once()



# =========================================================
# _internal_producer_task
# =========================================================

@pytest.mark.asyncio
async def test_internal_producer_task_normal_stream(
    chat_message_use_case,
    mock_assistant_service,
    mock_chat_message_service,
    mock_stream_lock_service,
):
    """
    1. 정상적인 모델 스트림 응답을 준비한다
    2. _internal_producer_task 를 호출한다
    3. assistant 메시지가 DB 에 저장된다
    """

    # 1.
    TEST_CHAT_ID = 1
    TEST_USER_ID = uuid.uuid4()
    TEST_REQUEST_ID = uuid.uuid4()

    TEST_REQUEST = MagicMock()
    TEST_REQUEST.request_id = TEST_REQUEST_ID

    TEST_CONTENTS = []
    TEST_METADATA = ChatMessageMetadata()

    mock_assistant_service.get_model_stream_response.return_value = async_chunk_generator(DEFAULT_CHUNKS)

    TEST_STATUS = MagicMock()
    TEST_STATUS.status = ChatStreamStatus.IS_STREAMING

    mock_stream_lock_service.check_status.return_value = TEST_STATUS

    # 2.
    await chat_message_use_case._internal_producer_task(
        req=TEST_REQUEST,
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        contents=TEST_CONTENTS,
        metadata=TEST_METADATA,
    )

    # 3.
    mock_chat_message_service.create_assistant_message.assert_called_once()
