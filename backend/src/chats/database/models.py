# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from __future__ import annotations

import uuid

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database.base import Base
from common.database.mixin import TimestampMixin, TimestampMixinCreate

if TYPE_CHECKING:
    from goals.database.models import GoalModel
    from problems.database.models import ProblemModel
    from users.database.models import UserModel

class ChatModel(Base, TimestampMixinCreate):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    latest_used_at: Mapped[datetime] = mapped_column()
    grade: Mapped[int]
    subject: Mapped[str] = mapped_column(String(50))

    chat_problems: Mapped[list[ChatProblemModel]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    goal: Mapped[GoalModel] = relationship(back_populates="chat")
    messages: Mapped[list[ChatMessageModel]] = relationship(back_populates="chat")


class ChatProblemModel(Base, TimestampMixin):
    __tablename__ = "chat_problem"

    __table_args__ = (
        UniqueConstraint("chat_id", "problem_id", name="uc_chat_id_problem_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    problem_id: Mapped[str] = mapped_column(ForeignKey("problem.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"))
    status: Mapped[str] = mapped_column(String(10))
    last_answer: Mapped[str | None] = mapped_column(Text)
    number: Mapped[int]

    is_bookmarked: Mapped[bool] = mapped_column(default=False, index=True)
    bookmarked_at: Mapped[datetime | None]

    chat: Mapped[ChatModel] = relationship(back_populates="chat_problems")
    problem: Mapped[ProblemModel] = relationship(back_populates="chat_problems")
    user: Mapped[UserModel] = relationship(back_populates="chat_problems")


class ChatMessageModel(Base, TimestampMixinCreate):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    type: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    meta_data: Mapped[str] = mapped_column(Text)

    chat: Mapped[ChatModel] = relationship(back_populates="messages")
