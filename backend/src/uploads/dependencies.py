# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import cast

from fastapi import Depends, Request

from uploads.service.i_upload_storage import IUploadStorageService
from uploads.usecase.upload_usecase import UploadUseCase


async def get_object_storage(
    request: Request
) -> IUploadStorageService:
    return cast(IUploadStorageService, request.app.state.object_storage)


async def get_upload_usecase(
    object_storage: IUploadStorageService = Depends(get_object_storage),
) -> UploadUseCase:
    return UploadUseCase(
        object_storage=object_storage
    )
