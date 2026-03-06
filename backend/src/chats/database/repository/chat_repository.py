# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


import uuid

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from base_repository import BaseRepoFilter, BaseRepository
from sqlalchemy import case, func, or_, select

from chats.database.models import ChatModel, ChatProblemModel
from chats.domain.chat import Chat, ChatDetail
from goals.database.models import GoalModel
from goals.domain.goal import GoalStatus
from problems.domain.problem import SubjectEnum


@dataclass(slots=True)
class ChatFilter(BaseRepoFilter):
    id: int | Iterable[int] | None = None
    user_id: uuid.UUID | Iterable[uuid.UUID] | None = None
    subject: SubjectEnum | list[SubjectEnum] | None = None


class ChatRepository(BaseRepository[ChatModel, Chat]):
    filter_class=ChatFilter


    async def get_chat_list(
        self,
        flt: ChatFilter,
        *,
        cursor_latest_used_at: datetime | None = None,
        cursor_id: int | None = None,
        size: int,
    ) -> list[ChatDetail]:
        """
        ChatFilter 조건을 만족하는 채팅 목록을 latest_used_at 기준으로 커서 페이지네이션하여 조회합니다.
        has_problem 및 has_active_goal 플래그를 계산하여 ChatDetail DTO로 반환합니다.
        """

        # 1. SELECT 절: 필요한 필드 및 계산된 플래그 선택
        select_fields = [            # has_problem 계산
            func.coalesce(
                func.max(case((ChatProblemModel.id.isnot(None), True), else_=False)),
                False
            ).label(ChatDetail.FIELD_HAS_PROBLEM),

            # has_active_goal 계산
            func.coalesce(
                func.max(case((GoalModel.status == GoalStatus.ACTIVE.value, True), else_=False)),
                False
            ).label(ChatDetail.FIELD_HAS_ACTIVE_GOAL),
        ]

        # 2. FROM, JOIN 및 기본 WHERE (user_id) 설정
        stmt = (
            select(ChatModel, *select_fields)
            .outerjoin(ChatProblemModel, ChatProblemModel.chat_id == ChatModel.id)
            .outerjoin(GoalModel, GoalModel.chat_id == ChatModel.id)
            .group_by(ChatModel.id)
        )

        # 3. ChatFilter 조건 적용
        crit = flt.where_criteria(self.model)
        if crit:
            stmt = stmt.where(*crit)

        # 4. 커서 기반 페이지네이션 (latest_used_at 기준)
        if cursor_latest_used_at and cursor_id:
            cursor_filter = or_(
                ChatModel.latest_used_at < cursor_latest_used_at,
                (ChatModel.latest_used_at == cursor_latest_used_at)
                & (ChatModel.id < cursor_id),
            )
            stmt = stmt.where(cursor_filter)

        # 5. 정렬 및 제한
        stmt = stmt.order_by(
            ChatModel.latest_used_at.desc(),
            ChatModel.id.desc()
        ).limit(size)

        # 6. 실행 및 ChatDetail DTO 변환
        s = self._resolve_session(None)
        rows = await s.execute(stmt)

        result = rows.unique().all()
        chats_detail = []
        for row, has_p, has_g in result:
            chat_model = row
            data = chat_model.__dict__
            data[ChatDetail.FIELD_HAS_PROBLEM] = has_p
            data[ChatDetail.FIELD_HAS_ACTIVE_GOAL] = has_g

            chats_detail.append(ChatDetail.model_validate(data))

        return chats_detail
