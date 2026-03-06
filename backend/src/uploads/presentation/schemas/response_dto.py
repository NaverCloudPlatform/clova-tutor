# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from pydantic import BaseModel


class UploadUrlResponse(BaseModel):
    presigned_url: str
    file_url: str
