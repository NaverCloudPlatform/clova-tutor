# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict
from typing_extensions import Doc


class CommonBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class IntIdMixin(BaseModel):
    FIELD_ID: ClassVar[str] = "id"

    id: Annotated[
        int,
        Doc(
            "자동 증가(AUTO_INCREMENT) 기본 키 필드입니다. "
            "기본값 0은 객체 생성 시 타입 및 초기화를 위한 자리표시자이며, "
            "실제 값은 DB INSERT 시 자동으로 채워집니다. "
            "이미 존재하는 레코드를 갱신할 때는 기존 ID 값을 사용합니다."
        )
    ] = 0
