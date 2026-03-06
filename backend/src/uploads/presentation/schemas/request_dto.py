# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from pydantic import BaseModel


class UploadUrlRequest(BaseModel):
    mime_type: str
