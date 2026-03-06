# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from typing import Annotated, ClassVar
from uuid import UUID

from typing_extensions import Doc

from common.domain.schema import CommonBase


class User(CommonBase):
    FIELD_NAME: ClassVar[str] = "name"
    FIELD_GRADE: ClassVar[str] = "grade"
    FIELD_MEMO: ClassVar[str] = "memo"

    id: Annotated[UUID, Doc("유저 ID / UUID")]
    name: Annotated[str, Doc("유저 이름")]
    grade: Annotated[int, Doc("유저 학년")]
    memo: Annotated[str | None, Doc("유저 관련 메모")]


class UserWithDate(User):
    FIELD_CREATED_AT: ClassVar[str] = "created_at"
    FIELD_UPDATED_AT: ClassVar[str] = "updated_at"

    created_at: Annotated[datetime, Doc("유저 생성 날짜")]
    updated_at: Annotated[datetime, Doc("유저 관련 수정 날짜")]
