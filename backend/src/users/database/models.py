# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chats.database.models import ChatProblemModel
from common.database.base import Base
from common.database.mixin import TimestampMixin
from goals.database.models import GoalModel


class UserModel(Base, TimestampMixin):
    """사용자 정보를 저장하는 모델입니다.

    Attributes:
        id (str): 사용자 고유 식별자
        name (str): 사용자 이름
        grade (int): 학년
        unknown_concepts (List[UserUnknownConcept]): 사용자가 이해하지 못한 개념 목록
    """

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50))
    grade: Mapped[int]
    memo: Mapped[str | None] = mapped_column(String(1024))

    # ORM 관계
    unknown_concepts: Mapped[list[UserUnknownConceptModel]] = relationship(back_populates="user",cascade="all, delete-orphan") # 1 : N
    goals: Mapped[list[GoalModel]] = relationship(back_populates="user") # 1 : N
    chat_problems: Mapped[list[ChatProblemModel]] = relationship(back_populates="user")


class UserUnknownConceptModel(Base, TimestampMixin):
    """사용자가 이해하지 못한 개념 정보를 저장하는 모델입니다.

    Attributes:
        id (int): 고유 식별자
        user_id (str): 사용자 ID
        subject (str): 과목명
        key_concept (str): 주요 개념
        unknown_concept (str): 이해하지 못한 세부 개념
        unknown_concept_reason (str): 이해하지 못한 이유
        user (User): 연관된 사용자 객체
    """

    __tablename__ = "user_unknown_concept"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
    )

    subject: Mapped[str] = mapped_column(String(30))
    key_concept: Mapped[str] = mapped_column(String(100))
    unknown_concept: Mapped[str] = mapped_column(String(100))
    unknown_concept_reason: Mapped[str | None] = mapped_column(Text)

    # ORM 관계
    user: Mapped[UserModel] = relationship(back_populates="unknown_concepts")

    __table_args__ = (
        Index("idx_user_subject", "user_id", "subject"),
        # user_id + subject + key_concept 로 유일성 보장
        UniqueConstraint(
            "user_id",
            "subject",
            "key_concept",
            name="uq_user_subject_unknown",
        ),
    )
