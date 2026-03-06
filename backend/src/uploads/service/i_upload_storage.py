# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from abc import ABC, abstractmethod

from fastapi import UploadFile


class IUploadStorageService(ABC):
    @abstractmethod
    def generate_presigned_url(
        self,
        key: str,
        mime_type: str
    ) -> str:
        raise NotImplementedError()


    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def create_signature(
        self,
        key: str,
        mime_type: str,
        expiry_time: int
    ) -> str:
        ...

    @abstractmethod
    async def upload_file(
        self,
        key: str,
        file: UploadFile | bytes
    ) -> None:
        ...

    @abstractmethod
    def get_endpoint(self) -> str:
        raise NotImplementedError()
