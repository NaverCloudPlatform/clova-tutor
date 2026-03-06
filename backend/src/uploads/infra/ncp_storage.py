# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import cast

import boto3

from botocore.client import Config
from fastapi import UploadFile

from config.config import ObjectStorageConfig
from uploads.service.i_upload_storage import IUploadStorageService


class NCPStorage(IUploadStorageService):
    def __init__(
        self,
        config: ObjectStorageConfig
    ) -> None:
        self.config = config

        self.client = boto3.client( # type: ignore
            config.OS_SERVICE_NAME,
            region_name=config.OS_REGION_NAME,
            endpoint_url=config.OS_ENDPOINT_URL,
            aws_access_key_id=config.OS_ACCESS_KEY,
            aws_secret_access_key=config.OS_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )

    def generate_presigned_url(self, key: str, mime_type: str) -> str:
        put_url = self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.config.OS_BUCKET_NAME,
                "Key": key,
                "ContentType": mime_type,
                "ACL": "public-read",
            },
            ExpiresIn=3600,  # 1시간
        )
        return cast(str,put_url)

    def get_endpoint(self) -> str:
        return f"{self.config.OS_ENDPOINT_URL}/{self.config.OS_BUCKET_NAME}"


    def close(self) -> None:
        self.client.close()

    async def upload_file(
        self,
        key: str,
        file: bytes | UploadFile
    ) -> None:
        ...

    def create_signature(
        self,
        key: str,
        mime_type: str,
        expiry_time: int
    ) -> str:
        return ""
