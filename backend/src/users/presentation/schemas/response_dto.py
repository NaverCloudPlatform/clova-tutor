# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from common.domain.schema import CommonBase


# User 기본 응답 모델
class UserResponse(CommonBase):
    id: UUID
    name: str
    grade: int
    memo: str | None
    created_at: datetime
    updated_at: datetime


class UserCreateResponse(BaseModel):
    id: UUID
    name: str
    grade: int
    memo: str | None


class UserUpdateResponse(BaseModel):
    id: UUID
    name: str
    grade: int
    memo: str | None


# Unknown Concept 기본 응답 모델
class UnknownConceptResponse(CommonBase):
    id: int
    subject: str
    key_concept: str
    unknown_concept: str
    unknown_concept_reason: str | None = None
    created_at: datetime
    updated_at: datetime
