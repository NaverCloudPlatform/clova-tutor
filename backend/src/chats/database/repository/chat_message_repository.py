# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import Iterable
from dataclasses import dataclass

from base_repository import BaseRepoFilter, BaseRepository
from sqlalchemy import exists as sa_exists
from sqlalchemy import select

from chats.database.models import ChatMessageModel
from chats.database.repository.chat_message_mapper import ChatMessageMapper
from chats.domain.chat_message.chat_message import ChatMessage, MessageRole


@dataclass(slots=True)
class ChatMessageFilter(BaseRepoFilter):
    chat_id: int | Iterable[int] | None = None

    role: MessageRole | Iterable[MessageRole] | None = None


class ChatMessageRepository(BaseRepository[ChatMessageModel, ChatMessage]):
    filter_class=ChatMessageFilter
    mapper=ChatMessageMapper

    async def exists(self, flt: ChatMessageFilter) -> bool:
        select_stmt = select(self.model)

        crit = flt.where_criteria(self.model)
        if crit:
            select_stmt = select_stmt.where(*crit)

        stmt = sa_exists(select_stmt.subquery()).select()
        s = self._resolve_session(None)
        res = await s.execute(stmt)
        return res.scalars().first() or False
