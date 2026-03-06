# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from common.service.exceptions import BaseAppException


class UploadException(BaseAppException):
    """업로드 관련 예외의 기본 클래스입니다."""
    default_msg = "업로드 오류가 발생했습니다."


class InvalidMimeTypeException(UploadException):
    """지원하지 않는 mime type을 요청했을 때 발생하는 예외"""

    def __init__(self, mime_type: str):
        msg = f"{mime_type} 형식은 지원하지 않습니다."
        super().__init__(
            msg=msg,
            data={"mime_type" : mime_type}
        )

class EmptyFileException(UploadException):
    default_msg = "빈 파일 컨텐츠가 들어왔습니다."
