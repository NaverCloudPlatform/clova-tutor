# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uploads.service.exceptions import UploadException


class InvalidSignatureException(UploadException):
    default_msg = "시그니처가 맞지 않습니다."


class ExpiredRequestException(UploadException):
    default_msg = "업로드할 수 있는 시간이 지났습니다."
