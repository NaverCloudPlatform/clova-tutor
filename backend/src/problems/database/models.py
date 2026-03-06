# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database.base import Base
from common.database.mixin import TimestampMixin

if TYPE_CHECKING:
    from chats.database.models import ChatProblemModel



class ProblemModel(Base, TimestampMixin):
    """
    문제 테이블
    - 문제 유형(type)에 따라 객관식(단일/다중), 주관식(단답형) 등으로 구분
    """

    __tablename__ = "problem"

    id: Mapped[str] = mapped_column(String(50),primary_key=True)

    subject: Mapped[str] = mapped_column(String(50), index=True)
    url: Mapped[str | None] = mapped_column(String(2048))
    grade: Mapped[int]
    semester: Mapped[int | None]
    level: Mapped[int]

    primary: Mapped[str | None] = mapped_column(String(255))
    secondary: Mapped[str | None] = mapped_column(String(255))
    specific: Mapped[str | None] = mapped_column(String(255))

    category: Mapped[str | None] = mapped_column(Text)
    problem: Mapped[str] = mapped_column(Text)
    choices: Mapped[str | None] = mapped_column(Text)

    correct_answers: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    hint: Mapped[str | None] = mapped_column(Text)

    tags: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50))

    # ORM 관계
    chat_problems: Mapped[ChatProblemModel] = relationship(back_populates="problem")
