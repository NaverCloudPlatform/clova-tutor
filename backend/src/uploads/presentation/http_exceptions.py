# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# FastAPI 애플리케이션에 예외 처리 핸들러를 등록하는 함수
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from common.presentation.response import http_error
from uploads.service.exceptions import EmptyFileException, InvalidMimeTypeException
from uploads.usecase.exceptions import ExpiredRequestException, InvalidSignatureException


def add_uploads_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidMimeTypeException)
    async def invalid_mime_type_handler(
        request: Request, exc: InvalidMimeTypeException
    ) -> JSONResponse:
        return http_error(400, exc)

    @app.exception_handler(EmptyFileException)
    async def empty_file_handler(
        request: Request, exc: EmptyFileException
    ) -> JSONResponse:
        return http_error(400, exc)

    @app.exception_handler(InvalidSignatureException)
    async def signature_not_correct_handler(
        request: Request, exc: InvalidSignatureException
    ) -> JSONResponse:
        return http_error(400, exc)


    @app.exception_handler(ExpiredRequestException)
    async def time_expiration_handler(
        request: Request, exc: ExpiredRequestException
    ) -> JSONResponse:
        return http_error(400, exc)
