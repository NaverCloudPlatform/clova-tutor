# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


from collections.abc import Iterable

from chats.database.models import ChatMessageModel
from chats.database.repository.chat_message_repository import (
    ChatMessageFilter,
    ChatMessageRepository,
)
from chats.domain.chat_message.chat_message import (
    ChatMessage,
    ChatMessageWithDate,
    MessageRole,
    MessageType,
)
from chats.domain.chat_message.message_content import (
    ChatMessageContent,
)
from chats.domain.chat_message.metadata import ChatMessageMetadata
from chats.domain.chat_message.system_content import SystemMessageContent
from chats.service.chat_service import ChatService


class ChatMessageService:
    def __init__(
        self,
        chat_service: ChatService,
        chat_message_repo: ChatMessageRepository,
    ):
        self.chat_service = chat_service
        self.chat_message_repo = chat_message_repo

    async def exists_by_chat_id(
        self,
        chat_id: int,
        *,
        role: Iterable[MessageRole]
    ) -> bool:
        return await self.chat_message_repo.exists(flt=ChatMessageFilter(
            chat_id=chat_id,
            role=role
        ))


    async def get_chat_messages(
        self,
        chat_id: int
    ) -> list[ChatMessageWithDate]:
        messages = await self.chat_message_repo.get_list(
            flt=ChatMessageFilter(chat_id=chat_id), convert_schema=False
        )

        msgs_with_date: list[ChatMessageWithDate] = []
        for msg in messages:
            cm = self.chat_message_repo._convert(msg, convert_schema=None)

            msgs_with_date.append(ChatMessageWithDate(
                **cm.model_dump(),
                created_at=msg.created_at
            ))

        return msgs_with_date

    async def get_latest_message(
        self,
        chat_id: int
    ) -> ChatMessageWithDate | None:
        messages = await self.chat_message_repo.get_list(
            flt=ChatMessageFilter(chat_id=chat_id),
            order_by=[ChatMessageModel.created_at.desc()],
            size=1,
            convert_schema=False
        )

        if len(messages) == 0:
            return None

        cm = self.chat_message_repo._convert(messages[0], convert_schema=True)

        return ChatMessageWithDate(
            **cm.model_dump(),
            created_at=messages[0].created_at
        )

    async def create_system_message(
        self,
        chat_id: int,
        contents: list[SystemMessageContent]
    ) -> ChatMessage:
        sys_msg = ChatMessage(
            chat_id=chat_id,
            type=MessageType.SYSTEM,
            role=MessageRole.SYSTEM,
            content=contents,
            meta_data=ChatMessageMetadata()
        )
        return await self.chat_message_repo.create(sys_msg)

    async def create_user_message(
        self,
        chat_id: int,
        contents: list[ChatMessageContent],
        metadata: ChatMessageMetadata
    ) -> ChatMessage:
        chat_msg = ChatMessage(
            chat_id=chat_id,
            type=MessageType.CHAT,
            role=MessageRole.USER,
            content=contents,
            meta_data=metadata
        )
        created = await self.chat_message_repo.create(chat_msg, convert_schema= False)
        await self.chat_service.update_chat_latest_used_at(chat_id, created.created_at)
        return self.chat_message_repo._convert(created, convert_schema=None)

    async def create_assistant_message(
        self,
        chat_id: int,
        contents:list[ChatMessageContent],
        metadata: ChatMessageMetadata
    ) -> ChatMessage:
        chat_msg = ChatMessage(
            chat_id=chat_id,
            type=MessageType.CHAT,
            role=MessageRole.ASSISTANT,
            content=contents,
            meta_data=metadata
        )

        created: ChatMessageModel = await self.chat_message_repo.create(chat_msg, convert_schema=False)
        await self.chat_service.update_chat_latest_used_at(chat_id, created.created_at)
        return self.chat_message_repo._convert(created, convert_schema=None)

