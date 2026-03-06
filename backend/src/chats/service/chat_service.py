# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime

from chats.database.repository.chat_repository import ChatFilter, ChatRepository
from chats.domain.chat import Chat, ChatDetail
from chats.service.exceptions import ChatNotFoundException
from problems.domain.problem import GradeEnum, SubjectEnum


class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository
    ) -> None:
        self.chat_repo = chat_repo


    async def get_chat_by_id(self, chat_id: int) -> Chat:
        chat: Chat | None = await self.chat_repo.get(flt=ChatFilter(id=chat_id))
        if chat is None:
            raise ChatNotFoundException(chat_id)
        return chat


    async def get_chat_list(
        self,
        user_id: uuid.UUID,
        subject_list: list[SubjectEnum] | None = None,
        *,
        size: int = 10,
        cursor_latest_used_at: datetime | None = None,
        cursor_id: int | None = None
    ) -> list[ChatDetail]:
        chat_filter = ChatFilter(
            user_id=user_id,
        )

        if subject_list is not None and len(subject_list) > 0:
            chat_filter.subject = subject_list

        chat_details: list[ChatDetail] = await self.chat_repo.get_chat_list(
            flt=chat_filter,
            size=size,
            cursor_latest_used_at=cursor_latest_used_at,
            cursor_id=cursor_id
        )
        return chat_details


    async def update_chat_latest_used_at(
        self,
        chat_id: int,
        latest_used_at: datetime | None = None
    ) -> bool:
        if latest_used_at is None:
            latest_used_at = datetime.now()
        res = await self.chat_repo.update(flt=ChatFilter(id=chat_id), update={Chat.FIELD_LATEST_USED_AT : latest_used_at})
        if res > 0:
            return True
        return False


    async def create_chat(
        self,
        title: str,
        user_id: uuid.UUID,
        subject: SubjectEnum,
        grade: GradeEnum
    ) -> Chat:
        new_chat = Chat(
            title=title,
            user_id=user_id,
            grade=grade,
            subject=subject,
            latest_used_at=datetime.now()
        )
        created: Chat = await self.chat_repo.create(new_chat)
        return created

    async def update_chat_title(
        self,
        chat_id: int,
        title: str
    ) -> Chat:
        chat_model = await self.chat_repo.get(flt=ChatFilter(id=chat_id), convert_schema=False)
        if chat_model is None:
            raise ChatNotFoundException(chat_id=chat_id)

        chat: Chat = await self.chat_repo.update_from_model(
            chat_model,
            update={
                Chat.FIELD_TITLE : title
            }
        )
        return chat

    async def delete_chat(
        self,
        chat_id: int
    ) -> None:
        await self.chat_repo.delete(flt=ChatFilter(id=chat_id))
