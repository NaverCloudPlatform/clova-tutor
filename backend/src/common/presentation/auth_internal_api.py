# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import Header, HTTPException, status

from config.config import internal_api_key


def verify_internal_api_key(x_api_key: str | None = Header(None)) -> None:
    if x_api_key != internal_api_key.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Key",
        )
