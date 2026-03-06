# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import secrets

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config.config import swagger_config

security = HTTPBasic()

async def swagger_authenticate(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    correct_username = secrets.compare_digest(credentials.username, swagger_config.SWAGGER_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, swagger_config.SWAGGER_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
