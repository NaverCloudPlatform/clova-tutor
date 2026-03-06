# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field
from typing_extensions import Doc

from common.domain.schema import CommonBase


class SystemMessageSubType(StrEnum):
    """시스템 메시지의 세부 타입을 정의하는 열거형 클래스입니다.

    Attributes:
        DATE: 날짜 구분선 메시지
    """
    DATE = "date"


class DateValue(CommonBase):
    text: Annotated[str, Doc("YYYY-MM-DD 형식의 날짜 문자열")]


class DateContent(CommonBase):
    m_type: Annotated[Literal[SystemMessageSubType.DATE], Doc("시스템 날짜 메시지 타입")]
    value: Annotated[DateValue, Doc("날짜 메시지 값")]


SystemMessageContent = Annotated[
    DateContent,
    Field(discriminator="m_type"),
]
