# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from typing import Annotated, ClassVar

from typing_extensions import Doc

from common.domain.schema import CommonBase


class AssistantRequest(CommonBase):
    FIELD_CHAT_ID: ClassVar[str] = "chat_id"
    FIELD_SBUJECT: ClassVar[str] = "subject"
    FIELD_GRADE: ClassVar[str] = "grade"
    FIELD_USER_ID: ClassVar[str] = "user_id"
    FIELD_USER_NAME: ClassVar[str] = "user_name"
    FIELD_USER_QUERY: ClassVar[str] = "user_query"
    FIELD_IMAGE_URL: ClassVar[str] = "image_url"
    FIELD_VECTOR_PROBLEM_ID: ClassVar[str] = "vector_problem_id"
    FIELD_TRANSLATION_BUTTON: ClassVar[str] = "translation_button"
    FIELD_REQUEST_ID: ClassVar[str] = "request_id"

    chat_id: Annotated[int,Doc("채팅 id")]
    subject: Annotated[str,Doc("과목명")]
    grade: Annotated[int,Doc("학년")]
    user_id: Annotated[uuid.UUID,Doc("유저 UUID")]
    user_name: Annotated[str,Doc("학생 이름")]
    user_query: Annotated[str,Doc("사용자 질의")]
    image_url: Annotated[list[str] | None, Doc("이미지 URL")] = None
    vector_problem_id: Annotated[str | None,Doc("Vector DB ID")] = None
    translation_button: Annotated[bool,Doc("직독직해 버튼 클릭 여부")]
    request_id: Annotated[uuid.UUID, Doc("현재 발화에 대한 고유 ID")]
