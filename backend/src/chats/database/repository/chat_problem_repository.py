# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import cast
from uuid import UUID

from base_repository import BaseRepoFilter, BaseRepository
from sqlalchemy import exists as sa_exists
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from chats.database.models import ChatProblemModel
from chats.domain.chat import ChatDetail
from chats.domain.chat_problem import (
    ChatProblem,
    ChatProblemDetail,
    ChatProblemWithChatDetailAndWithProblem,
)
from goals.database.models import GoalModel
from goals.domain.goal import GoalStatus
from problems.database.models import ProblemModel
from problems.database.problem_mapper import ProblemMapper
from problems.domain.problem import SubjectEnum


@dataclass
class ChatProblemFilter(BaseRepoFilter):
    id: int | Iterable[int]|  None = None
    chat_id: int | Iterable[int] | None = None
    problem_id: str | Iterable[str] | None = None
    user_id: UUID | Iterable[UUID] | None = None
    status: str | Iterable[str] | None = None
    is_bookmarked: bool | Iterable[bool] | None = None

class ChatProblemRepository(BaseRepository[ChatProblemModel, ChatProblem]):
    filter_class=ChatProblemFilter

    async def exists(self, flt: ChatProblemFilter) -> bool:
        select_stmt = select(self.model)

        crit = flt.where_criteria(self.model)
        if crit:
            select_stmt = select_stmt.where(*crit)

        stmt = sa_exists(select_stmt.subquery()).select()
        s = self._resolve_session(None)
        res = await s.execute(stmt)
        return res.scalars().first() or False

    async def get_with_problems(self, flt: ChatProblemFilter) -> list[ChatProblemDetail]:
        select_stmt = select(self.model)

        crit = flt.where_criteria(self.model)
        select_stmt = select_stmt.where(*crit).options(
            selectinload(ChatProblemModel.problem)
        )

        s = self._resolve_session(None)
        r = await s.execute(select_stmt)

        rows = r.scalars().all()

        res: list[ChatProblemDetail] = []

        _pm = ProblemMapper()
        for row in rows:
            cp = self._convert(row, convert_schema=None)
            res.append(
                ChatProblemDetail(
                    **cp.model_dump(),
                    problem=_pm.to_schema(row.problem)
                )
            )

        return res

    async def get_bookmarked_problems(
        self,
        flt: ChatProblemFilter,
        subject_filter: Iterable[SubjectEnum] | None = None,
        *,
        cursor_bookmarked_at: datetime | None = None,
        size: int = 10
    ) -> list[ChatProblemWithChatDetailAndWithProblem]:

        # has_active_goal
        has_active_goal_exists = (
            select(GoalModel.id)
            .where(GoalModel.chat_id == ChatProblemModel.chat_id)
            .where(GoalModel.status == GoalStatus.ACTIVE.value)
        ).exists().label(ChatDetail.FIELD_HAS_ACTIVE_GOAL)

        crit = flt.where_criteria(self.model)

        if cursor_bookmarked_at:
            # created_at이 커서보다 '이전'인 데이터만 조회합니다. (역순 정렬을 전제로 함)
            crit.append(ChatProblemModel.bookmarked_at < cursor_bookmarked_at)

        if subject_filter:
            crit.append(ProblemModel.subject.in_(subject_filter))

        stmt = (
            select(self.model, has_active_goal_exists)
            .join(ProblemModel)
            .where(*crit)
            .options(
                selectinload(ChatProblemModel.problem),
                selectinload(ChatProblemModel.chat)
            )
            .order_by(
                ChatProblemModel.bookmarked_at.desc()
            )
            .limit(size)
        )

        s = self._resolve_session(None)
        r = await s.execute(stmt)

        rows = cast(Sequence[tuple[ChatProblemModel, bool]],r.unique().all())
        res: list[ChatProblemWithChatDetailAndWithProblem] = []

        _pm = ProblemMapper()
        for row, has_g in rows:
            cp = self._convert(row, convert_schema=None)
            p = _pm.to_schema(row.problem)
            res.append(
                ChatProblemWithChatDetailAndWithProblem(
                    **cp.model_dump(),
                    problem=p,
                    chat=ChatDetail(
                        **row.chat.__dict__,
                        has_problem=True,
                        has_active_goal=has_g
                    )
                )
            )

        return res
