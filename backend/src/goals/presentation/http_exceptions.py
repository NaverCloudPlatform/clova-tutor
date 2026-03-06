# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from common.presentation.response import http_error
from goals.service.exceptions import (
    InvalidGoalValueExeception,
    NotFoundGoalException,
)
from goals.usecase.exceptions import ActiveGoalExistException


def add_goal_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundGoalException)
    async def handle_goal_notfound(request: Request, exc: NotFoundGoalException) -> JSONResponse:
        return http_error(404, exc)

    @app.exception_handler(InvalidGoalValueExeception)
    async def handle_goal_invalid(request: Request, exc: InvalidGoalValueExeception) -> JSONResponse:
        return http_error(401, exc)

    @app.exception_handler(ActiveGoalExistException)
    async def handle_active_goal_exist(request: Request, exc: ActiveGoalExistException) -> JSONResponse:
        return http_error(400, exc)
