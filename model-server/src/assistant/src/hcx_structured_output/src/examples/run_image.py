# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# examples/run_image.py
import time

from src.schemas.image import ImageDescription
from src.utils import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    IMAGE_CAPTION_PROMPT_TEMPLATE,
    load_prompt_yaml,
    run_structured_task,
)

SYSTEM_RULES, FEWSHOTS = load_prompt_yaml("../prompt/prompt_image.yaml")

if __name__ == "__main__":
    user_text = IMAGE_CAPTION_PROMPT_TEMPLATE
    image_url = "https://drive.usercontent.google.com/download?id=1LSiG8wehykHLYswk3j5tqh2aJRurruXY&export=view"

    multimodal_user = {
        "role": "user",
        "content": [
            {"type": "text", "text": user_text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ],
    }
    start = time.time()
    res = run_structured_task(
        system_rules=SYSTEM_RULES,
        fewshots=FEWSHOTS,
        user_content=multimodal_user,
        response_model=ImageDescription,
        model=DEFAULT_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        max_retries=DEFAULT_MAX_RETRIES,
    )
    print("✅ Done", f"{time.time()-start:.2f}s")
    print(res.model_dump())
