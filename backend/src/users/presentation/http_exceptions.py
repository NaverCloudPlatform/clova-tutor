# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from common.presentation.response import http_error
from users.service.exceptions import UserNotFoundException


def add_users_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request: Request, exc: UserNotFoundException) -> JSONResponse:
        return http_error(404, exc)
