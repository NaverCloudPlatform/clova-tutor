# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/tasks/__init__.py
"""High-level task functions for common structured output use cases."""

from .image_caption import run_image_caption
from .translation import run_bilingual_segments

__all__ = ["run_image_caption", "run_bilingual_segments"]
