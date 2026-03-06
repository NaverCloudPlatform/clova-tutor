# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from typing import Annotated, ClassVar
from uuid import UUID

from typing_extensions import Doc

from common.domain.schema import CommonBase, IntIdMixin


class UserUnknownConcept(CommonBase, IntIdMixin):
    FIELD_USER_ID: ClassVar[str] = "user_id"
    FIELD_SUBJECT: ClassVar[str] = "subject"
    FIELD_KEY_CONCEPT: ClassVar[str] = "key_concept"
    FIELD_UNKNOWN_CONCEPT: ClassVar[str] = "unknown_concept"
    FIELD_UNKNOWN_CONCEPT_REASON: ClassVar[str] = "unknown_concept_reason"


    user_id: Annotated[UUID, Doc("사용자 Id - UUID")]
    subject: Annotated[str, Doc("과목명 - str")]
    key_concept: Annotated[str, Doc("해당 과목 내 주요 개념(대단원) - str")]
    unknown_concept: Annotated[str, Doc("실제로 모르는 세부 개념 - str")]
    unknown_concept_reason: Annotated[str | None, Doc("이유, 상황 등.. - str | None")]

class UserUnknownConceptWithDate(UserUnknownConcept):
    FIELD_UNKNOWN_CREATED_AT: ClassVar[str] = "created_at"
    FIELD_UNKNOWN_UPDATED_AT: ClassVar[str] = "updated_at"

    created_at: Annotated[datetime, Doc("생성 날짜")]
    updated_at: Annotated[datetime, Doc("수정 날짜")]

