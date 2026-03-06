# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from auths.service.exceptions import HeaderNotExistException, HeaderTypeNotMatchException
from common.presentation.response import http_error


def add_auths_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HeaderNotExistException)
    async def header_not_exist_handler(request: Request, exc: HeaderNotExistException) -> JSONResponse:
        return http_error(401, exc)

    @app.exception_handler(HeaderTypeNotMatchException)
    async def header_type_not_match_handler(request: Request, exc: HeaderTypeNotMatchException) -> JSONResponse:
        return http_error(400, exc)
