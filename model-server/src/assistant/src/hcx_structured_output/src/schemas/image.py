# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/schemas/image.py
from pydantic import Field

from .primitives import SingleKeyModel


class ImageDescription(SingleKeyModel):
    image_description: str = Field(min_length=1)


__all__ = ["ImageDescription"]
