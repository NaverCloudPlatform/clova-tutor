# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from common.service.exceptions import BaseAppException


class ErrorResponse(BaseModel):
    message: str
    detail: dict[str, Any] | None = None


def http_error(status_code: int, exc: BaseAppException) -> JSONResponse:
    resp = JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            message=exc.msg,
            detail={"kind": exc.kind, "data": exc.data}
        ).model_dump()
    )

    return resp
