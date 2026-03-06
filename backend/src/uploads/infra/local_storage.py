# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import hashlib
import hmac
import os
import time

from urllib.parse import urlencode

from fastapi import UploadFile

from config.config import LocalStorageConfig
from uploads.service.exceptions import EmptyFileException
from uploads.service.i_upload_storage import IUploadStorageService


class LocalStorage(IUploadStorageService):
    def __init__(
        self,
        config: LocalStorageConfig
    ) -> None:
        self.base_url = config.BASE_URL
        self._secret_key = config.SECRET_KEY
        self.url_expiry_seconds = config.URL_EXPIRY_SECONDS
        self.upload_dir = config.UPLOAD_DIR

    async def upload_file(
        self,
        key: str,
        file: UploadFile | bytes
    ) -> None:
        local_path = os.path.join(self.upload_dir, key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # 파일 읽기
        if isinstance(file, UploadFile):
            file_content = await file.read()
        elif isinstance(file, bytes):
            file_content = file

        if not file_content:
            raise EmptyFileException()

        with open(local_path, "wb") as f:
            f.write(file_content)


    def get_endpoint(self) -> str:
        return f"{self.base_url}/{self.upload_dir}"


    def create_signature(self, key: str, mime_type: str, expiry_time: int) -> str:
        data = f"{key}|{mime_type}|{expiry_time}"
        return hmac.new(
            self._secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()


    def generate_presigned_url(
        self,
        key: str,
        mime_type: str
    ) -> str:
        expiry_time = int(time.time()) + self.url_expiry_seconds
        sig = self.create_signature(key, mime_type, expiry_time)

        params = {
            "expires" : expiry_time,
            "signature" : sig,
            "mime" : mime_type
        }
        query_string = urlencode(params)
        put_url = f"{self.base_url}/uploads/{key}?" + query_string

        return put_url

    def close(self) -> None:
        ...
