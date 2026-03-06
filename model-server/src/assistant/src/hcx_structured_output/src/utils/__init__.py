# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/utils/__init__.py
"""Utility functions for HCX structured output."""

from .chunk import split_text

# Only expose constants and simple utilities to avoid circular imports
from .constants import (
    DEFAULT_MAX_CHARS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    GENERIC_PROMPT_TEMPLATE,
    IMAGE_CAPTION_PROMPT_TEMPLATE,
    TRANSLATION_PROMPT_TEMPLATE,
)
from .load_utils import load_api_config, load_prompt_yaml, load_yaml
from .merge import merge_pydantic_models

# Import runner after fixing circular dependency
from .runner import run_structured_task, with_structured_output_like

__all__ = [
    "run_structured_task",
    "with_structured_output_like",
    "load_prompt_yaml",
    "load_yaml",
    "load_api_config",
    "split_text",
    "merge_pydantic_models",
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_MAX_CHARS",
    "IMAGE_CAPTION_PROMPT_TEMPLATE",
    "TRANSLATION_PROMPT_TEMPLATE",
    "GENERIC_PROMPT_TEMPLATE",
]
