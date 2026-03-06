# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import time
import uuid

from fastapi import UploadFile

from uploads.presentation.schemas.request_dto import UploadUrlRequest
from uploads.presentation.schemas.response_dto import UploadUrlResponse
from uploads.service.exceptions import InvalidMimeTypeException
from uploads.service.i_upload_storage import IUploadStorageService
from uploads.usecase.exceptions import (
    ExpiredRequestException,
    InvalidSignatureException,
)
from uploads.utils.constants import MIME_EXT_MAP


class UploadUseCase:
    def __init__(
        self,
        object_storage: IUploadStorageService
    ) -> None:
        self.object_storage = object_storage

    async def get_upload_url(
        self, upload_req: UploadUrlRequest
    ) -> UploadUrlResponse:
        mime_type = upload_req.mime_type
        if mime_type not in MIME_EXT_MAP:
            raise InvalidMimeTypeException(mime_type)

        ext = MIME_EXT_MAP.get(mime_type, "png")
        file_name = f"{uuid.uuid4()}.{ext}"


        put_url = self.object_storage.generate_presigned_url(
            key=f"chat-upload/{file_name}", mime_type=mime_type
        )

        url = f"{self.object_storage.get_endpoint()}/chat-upload/{file_name}"

        return UploadUrlResponse(presigned_url=put_url, file_url=url)

    async def upload_file(
        self,
        key: str,
        expires: int,
        signature: str,
        mime_type: str,
        file: bytes | UploadFile,
    ) -> None:
        """
        # 1. 서명 확인
        # 2. 시간 지났는지 확인
        # 3. 파일 업로드

        """
        expected_sig = self.object_storage.create_signature(key, mime_type, expires)
        if expected_sig != signature:
            raise InvalidSignatureException()

        current_time = int(time.time())
        if current_time > expires:
            raise ExpiredRequestException()

        await self.object_storage.upload_file(
            key=key,
            file=file
        )
