# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

"""
HCX Structured Output Package

Utilities and examples to get structured output from HyperCLOVA X via Instructor.
"""

__version__ = "0.1.0"

# Import schemas
from .schemas import (
    AtLeastOneSegments,
    ImageDescription,
    Segments,
    build_model_from_spec,
)

# Import high-level task functions
from .tasks import run_bilingual_segments, run_image_caption

# Import main utilities for easy access
from .utils import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    GENERIC_PROMPT_TEMPLATE,
    IMAGE_CAPTION_PROMPT_TEMPLATE,
    TRANSLATION_PROMPT_TEMPLATE,
    load_prompt_yaml,
    run_structured_task,
    with_structured_output_like,
)

__all__ = [
    # Core utilities
    "run_structured_task",
    "load_prompt_yaml",
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_RETRIES",
    "TRANSLATION_PROMPT_TEMPLATE",
    "IMAGE_CAPTION_PROMPT_TEMPLATE",
    "GENERIC_PROMPT_TEMPLATE",
    "with_structured_output_like",
    # Schemas
    "build_model_from_spec",
    "ImageDescription",
    "Segments",
    "AtLeastOneSegments",
    # High-level tasks
    "run_image_caption",
    "run_bilingual_segments",
]
