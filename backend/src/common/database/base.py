# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """subclasses will be converted to dataclasses"""
