# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from base_repository import BaseRepoFilter, BaseRepository
from sqlalchemy import exists as sa_exists
from sqlalchemy import select

from goals.database.models import GoalModel
from goals.domain.goal import Goal, GoalStatus


@dataclass(slots=True)
class GoalFilter(BaseRepoFilter):
    id: int | Iterable[int] | None = None

    # 채팅 id
    chat_id: int | Iterable[str] | None = None

    # 과목
    subject: str | Iterable[str] |None = None

    # 사용자 UUID
    user_id: UUID | Iterable[UUID] | None = None

    # 상태 리스트
    status: GoalStatus | Iterable[GoalStatus] | None = None


class GoalRepository(BaseRepository[GoalModel, Goal]):
    filter_class = GoalFilter

    async def exists(self, flt: GoalFilter) -> bool:
        select_stmt = select(self.model)

        crit = flt.where_criteria(self.model)
        if crit:
            select_stmt = select_stmt.where(*crit)

        stmt = sa_exists(select_stmt.subquery()).select()
        s = self._resolve_session(None)
        res = await s.execute(stmt)
        return res.scalars().first() or False
