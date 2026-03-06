# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import List, Dict, Any
from typing import Optional

from pydantic import BaseModel, Field

from common.schema import CommonBase


class StudentProfile(CommonBase):
    user_id: str
    name: str
    semester: Optional[int]
    grade: int


class Properties(BaseModel):
    message: str = Field(..., description="사용자 메시지 내용")
    image_url: Optional[str] = Field(..., description="이미지 URL")
    type: str = Field(..., description="메시지 유형")


class Vector(BaseModel):
    message: List[float] = Field(..., description="메시지 임베딩 벡터(실수 리스트)")


class References(BaseModel):
    user: str = Field(..., description="사용자 UUID")


class MessagePayload(BaseModel):
    properties: Properties = Field(..., description="기본 속성 정보")
    vector: Vector = Field(..., description="임베딩 정보")
    references: References = Field(..., description="참조 정보")


class ProblemCardPayload(BaseModel):
    parsed_card: Dict[str, Any]
    vector: Dict[str, Any]
    user_uuid: str


class MemoryPayload(BaseModel):
    note: Dict[str, Any]
    card_uuid: str


class DeleteResp(BaseModel):
    deleted: bool = True


class GetResp(BaseModel):
    data: Dict[str, Any]


class SearchPayload(BaseModel):
    index_name: str
    near_vector: List[float]
    k: int = 5
    target_vector: Optional[str] = None


class SetupResp(BaseModel):
    created: bool = True
