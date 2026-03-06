# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from pydantic import BaseModel, ConfigDict


class CommonBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
