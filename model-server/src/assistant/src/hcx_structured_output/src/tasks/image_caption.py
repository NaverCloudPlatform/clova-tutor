# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/tasks/image_caption.py
from ..schemas.image import ImageDescription
from ..utils.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    IMAGE_CAPTION_PROMPT_TEMPLATE,
)
from ..utils.load_utils import load_prompt_yaml
from ..utils.runner import run_structured_task


def run_image_caption(
    image_url: str,
    *,
    extra_instructions: str = "",
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_retries: int = DEFAULT_MAX_RETRIES,
):
    # Load prompt at runtime
    system_rules, fewshots = load_prompt_yaml("../prompt/prompt_image.yaml")

    user_text = IMAGE_CAPTION_PROMPT_TEMPLATE
    if extra_instructions:
        user_text += f"\n추가 지침:\n{extra_instructions}"

    return run_structured_task(
        system_rules=system_rules,
        fewshots=fewshots,
        user_content=user_text,
        response_model=ImageDescription,
        model=model,
        temperature=temperature,
        max_retries=max_retries,
        chunk_policy={"image_url": image_url},
    )
