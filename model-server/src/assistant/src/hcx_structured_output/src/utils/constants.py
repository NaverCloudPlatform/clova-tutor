# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/utils/constants.py
"""Common constants used across the package."""

# Model configurations
DEFAULT_MODEL = "HCX-005"
DEFAULT_TEMPERATURE = 0.01
DEFAULT_MAX_RETRIES = 20
DEFAULT_MAX_CHARS = 600

# Image caption prompt template
IMAGE_CAPTION_PROMPT_TEMPLATE = (
    "아래 이미지를 OCR+객관적 묘사 규칙에 따라 상세 기술하세요.\n"
    "응답은 오직 JSON 하나만, 키는 image_description 단 하나만 허용.\n"
    'schema: {"image_description":str}\n'
    "JSON 문자열 내부의 백슬래시/개행/탭은 반드시 이스케이프: \\\\, \\n, \\t.\n"
    "코드블록(```)을 사용하지 말고 순수 JSON만 출력하세요.\n"
)

# Translation prompt template
TRANSLATION_PROMPT_TEMPLATE = (
    "다음 텍스트를 '구절' 단위로 세밀하게 분할하고, en/ko 직독직해로 반환하세요.\n"
    "응답은 반드시 순수 JSON만, 코드블록(```) 없이 출력.\n"
    'schema: {"segments":[{"en":str,"ko":str}]}\n'
    "JSON 문자열 내부의 백슬래시/개행/탭은 반드시 이스케이프: \\\\, \\n, \\t.\n"
)

# Generic task prompt template
GENERIC_PROMPT_TEMPLATE = (
    "다음 문서에서 스키마에 맞춰 정보를 추출하세요.\n"
    "schema: {schema}\n"
    "응답은 반드시 순수 JSON만 출력하세요.\n"
    "코드블록(```)을 사용하지 말고 순수 JSON만 출력하세요.\n"
    "문서:\n"
)

__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_MAX_CHARS",
    "IMAGE_CAPTION_PROMPT_TEMPLATE",
    "TRANSLATION_PROMPT_TEMPLATE",
    "GENERIC_PROMPT_TEMPLATE",
]
