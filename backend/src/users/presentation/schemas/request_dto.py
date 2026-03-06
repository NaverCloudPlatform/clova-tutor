# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from pydantic import BaseModel, field_validator


# POST - /users
class UserCreateRequestBody(BaseModel):
    name: str
    grade: int
    memo: str | None = None

    @field_validator("memo", mode="before")
    @classmethod
    def validate_memo_len(cls, v: str | None) -> str | None:
        if isinstance(v, str) and len(v) > 1024:
            raise ValueError("memo는 1024자 이상 넘을 수 없습니다.")
        return v

# PATCH - /users/{user_id}
class UserUpdateRequestBody(BaseModel):
    name: str | None = None
    grade: int | None = None
    memo: str | None = None

    @field_validator("memo", mode="before")
    @classmethod
    def validate_memo_len(cls, v: str | None) -> str | None:
        if isinstance(v, str) and len(v) > 1024:
            raise ValueError("memo는 1024자 이상 넘을 수 없습니다.")
        return v


# POST - /users/{user_id}/unknown-concepts
class UnknownConceptCreateRequestBody(BaseModel):
    subject: str
    key_concept: str
    unknown_concept: str
    unknown_concept_reason: str | None = None

