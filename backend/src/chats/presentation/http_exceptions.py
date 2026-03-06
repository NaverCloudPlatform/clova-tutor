# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# FastAPI 애플리케이션에 예외 처리 핸들러를 등록하는 함수
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from chats.service.exceptions import (
    AlreadySolvedException,
    ChatAccessForbiddenException,
    ChatNotFoundException,
    ChatProblemNotFoundException,
    StreamTimeoutException,
)
from chats.usecase.exceptions import StreamAlreadyFinishException, StreamAlreadyInProgressException
from common.presentation.response import http_error


def add_chats_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ChatNotFoundException)
    async def chat_not_found_handler(request: Request, exc: ChatNotFoundException) -> JSONResponse:
        return http_error(404, exc)

    @app.exception_handler(ChatAccessForbiddenException)
    async def chat_access_forbidden_handler(
        request: Request, exc: ChatAccessForbiddenException
    ) -> JSONResponse:
        return http_error(403, exc)

    @app.exception_handler(ChatProblemNotFoundException)
    async def chat_problem_not_found_handler(
        request: Request, exc: ChatProblemNotFoundException
    ) -> JSONResponse:
        return http_error(404, exc)

    @app.exception_handler(AlreadySolvedException)
    async def already_solved_handler(request: Request, exc: AlreadySolvedException) -> JSONResponse:
        return http_error(400, exc)

    @app.exception_handler(StreamAlreadyFinishException)
    async def already_finished_handler(request: Request, exc: StreamAlreadyFinishException) -> JSONResponse:
        return http_error(400, exc)

    # ------------------------------
    # 스트림 관련 예외 핸들러
    # ------------------------------
    @app.exception_handler(StreamAlreadyInProgressException)
    async def stream_already_in_progress_handler(request: Request, exc: StreamAlreadyInProgressException) -> JSONResponse:
        return http_error(409, exc)

    @app.exception_handler(StreamTimeoutException)
    async def stream_timeout_handler(request: Request, exc: StreamTimeoutException) -> JSONResponse:
        return http_error(504, exc)

