# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from common.utils.circuit_breaker import CircuitOpenError


def app_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:

        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={"detail": "서비스 사용이 불가합니다."},
        )

    @app.exception_handler(CircuitOpenError)
    async def circuit_exception_handler(request: Request, exc: CircuitOpenError) -> JSONResponse:
        """
        디비 서킷브레이커가 차단했을때 발생하는 에러의 글로벌 핸들러입니다.
        """
        traceback.print_exc()

        # 사용자에게는
        return JSONResponse(
            status_code=500,
            content={"detail": "서비스 사용이 불가합니다."},
        )
