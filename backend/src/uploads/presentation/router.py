# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from common.presentation.response import ErrorResponse
from uploads.dependencies import get_upload_usecase
from uploads.presentation.schemas.request_dto import UploadUrlRequest
from uploads.presentation.schemas.response_dto import UploadUrlResponse
from uploads.usecase.upload_usecase import UploadUseCase

router = APIRouter()


@router.post(
    "",
    response_model=UploadUrlResponse,
    description="파일 업로드 위한 url을 반환합니다.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "지원하지 않는 mime type 요청 시 반환됩니다.",
        },
    },
)
async def create_upload_url(
    # Body
    upload_req: UploadUrlRequest,
    # 의존성
    usecase: UploadUseCase = Depends(get_upload_usecase),
) -> UploadUrlResponse:
    response = await usecase.get_upload_url(upload_req)
    return response


@router.put(
    "/{key:path}",
)
async def upload_file(
    # Path 파라미터
    key: str,
    # 쿼리 파라미터
    expires: int,
    signature: str,
    mime: str,
    # Body
    request: Request,
    # 의존성
    usecase: UploadUseCase = Depends(get_upload_usecase),
) -> JSONResponse:
    file_bytes = await request.body()

    await usecase.upload_file(
        key=key,
        expires=expires,
        signature=signature,
        mime_type=mime,
        file=file_bytes
    )
    return JSONResponse(content="OK")

