# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from common.infra.mysql.mysql import get_mysql


class DBMiddleware(BaseHTTPMiddleware):
    """
    api 요청(Request 객체) 시 데이터베이스 세션을 주입하는 미들웨어입니다.
    """
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        mysql = get_mysql()

        async with mysql.contextual_session():
            response = await call_next(request)
            return response

