# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from chats.database.repository.chat_message_repository import (
    ChatMessageFilter,
    ChatMessageRepository,
)
from chats.domain.chat_message.chat_message import ChatMessage, MessageRole, MessageType
from chats.domain.chat_message.metadata import ChatMessageMetadata


@pytest.fixture
def chat_message_repo(db_session: AsyncSession) -> ChatMessageRepository:
    return ChatMessageRepository(session=db_session)


# -----------------------------------------------------
# exists
# -----------------------------------------------------
@pytest.mark.asyncio
async def test_chat_message_exists_true(
    chat_message_repo: ChatMessageRepository,
):
    """
    1. 특정 chat_id로 메시지 생성
    2. exists 호출
    3. True 반환 확인
    """

    # 1.
    TEST_CHAT_ID = -1

    created_message = await chat_message_repo.create(
        ChatMessage(
            chat_id=TEST_CHAT_ID,
            type=MessageType.CHAT,
            role=MessageRole.SYSTEM,
            content=[],
            meta_data=ChatMessageMetadata(),
        )
    )

    # 2.
    exists_found = await chat_message_repo.exists(
        flt=ChatMessageFilter(chat_id=created_message.chat_id)
    )

    # 3.
    assert exists_found is True


@pytest.mark.asyncio
async def test_chat_message_exists_false(
    chat_message_repo: ChatMessageRepository,
):
    """
    1. DB에 존재하지 않는 chat_id 준비
    2. exists 호출
    3. False 반환 확인
    """

    # 1.
    NOT_EXIST_CHAT_ID = -999999

    # 2.
    exists_found = await chat_message_repo.exists(
        flt=ChatMessageFilter(chat_id=NOT_EXIST_CHAT_ID)
    )

    # 3.
    assert exists_found is False
