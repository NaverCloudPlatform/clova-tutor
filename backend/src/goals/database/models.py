# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from __future__ import annotations

import uuid

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database.base import Base
from common.database.mixin import TimestampMixin

if TYPE_CHECKING:
    from chats.database.models import ChatModel
    from users.database.models import UserModel


class GoalModel(Base, TimestampMixin):
    """
    채팅방에서의 목표를 저장하는 모델 클래스입니다.

    Attributes:
        id (int): 목표 ID
        subject (str) : 채팅 과목
        user_id (str) : 사용자 UUID
        chat_id (int) : 채팅 ID
        goal_count (int) : 목표 문제 수
        solved_count (int) : 현재 달성 문제 수
        finished_at (datetime | None) : 언제 끝났는지 시간
        status (str) : 끝났는지, 진행 중, 취소 로 나눔

        created_at (datetime) : 생성 날짜
        updated_at (datetime) : 수정 날짜
    """

    __tablename__ = "goal"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 과목
    subject: Mapped[str] = mapped_column(String(10))
    # 사용자 UUID, index 사용함
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    # 목표 달성 문제 개수
    goal_count: Mapped[int]
    # 현재 푼 문제 수
    solved_count: Mapped[int] = mapped_column(default=0)

    # 목표 달성 여부
    finished_at: Mapped[datetime | None] = mapped_column(default=None)

    # 현재 목표 상태 (Ref: GoalStatus)
    status: Mapped[str] = mapped_column(String(10))
    # 연관 관계

    chat: Mapped[ChatModel] = relationship(back_populates="goal", uselist=False) # 1: 1
    user: Mapped[UserModel] = relationship(back_populates="goals") # N : 1
