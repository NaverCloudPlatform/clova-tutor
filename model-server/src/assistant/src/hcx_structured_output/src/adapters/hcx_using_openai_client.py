# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/adapters/hcx_using_openai_client.py
import json
import re
from functools import lru_cache
from types import SimpleNamespace
from typing import Any, List, Optional

from openai import OpenAI

from ..utils.load_utils import load_api_config
from .utils import messages_to_text, next_attempt, pretty_json

config = load_api_config()
HCX_API_KEY = config["hcx-005"]["api_key"]
HCX_OPENAI_BASE_URL = config["HCX_OPENAI_BASE_URL"]


@lru_cache(maxsize=None)
def _get_openai_client(api_key: Optional[str] = None) -> OpenAI:
    key = api_key or HCX_API_KEY
    if not key:
        raise RuntimeError("HCX_API_KEY is not set")
    return OpenAI(api_key=key, base_url=HCX_OPENAI_BASE_URL)


_SINGLE_FIELD_OBJ = re.compile(
    r'^\s*\{\s*"(?P<key>[^"]+)"\s*:\s*"(?P<val>[\s\S]*)"\s*\}\s*$',
    re.DOTALL,
)


def _rebuild_single_field_json(text: str) -> Optional[str]:
    m = _SINGLE_FIELD_OBJ.match(text or "")
    if not m:
        return None
    key = m.group("key")
    raw_val = m.group("val")
    try:
        val = json.loads(f'"{raw_val}"')
    except Exception:
        return None
    return json.dumps({key: val}, ensure_ascii=False)


def _extract_text_from_openai_content(content: Any) -> str:
    """
    Extract text from OpenAI Chat Completions response message.content:
    """
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                parts.append(str(b.get("text", "")))
        return "\n".join([p for p in parts if p])
    return str(content)


def _parse_json_with_rebuild(content: str) -> Optional[str]:
    cleaned = (content or "").strip()

    # 1) remove code fences
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()

    # 2) parse directly
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return json.dumps(obj, ensure_ascii=False)
    except Exception:
        pass

    # 3) unwrap double-encoded string
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        try:
            unwrapped = json.loads(cleaned)
            if isinstance(unwrapped, str):
                obj2 = json.loads(unwrapped)
                if isinstance(obj2, dict):
                    return json.dumps(obj2, ensure_ascii=False)
        except Exception:
            pass

    # 4) rebuild single field object: {"key":"..."} → {"key": "..."} (escape normalization)
    rebuilt = _rebuild_single_field_json(cleaned)
    if rebuilt:
        try:
            obj3 = json.loads(rebuilt)
            if isinstance(obj3, dict):
                return json.dumps(obj3, ensure_ascii=False)
        except Exception:
            pass

    return None


# ── 3) instructor.patch(create=...) target function ─────────────────────────────────
def safe_openai_create(
    *,
    model: str,
    messages: List[dict],
    api_key: Optional[str] = None,
    **kwargs,
) -> Any:
    """
    - Direct call to HCX (OpenAI-compatible)
    - Remove incompatible parameters (response_format, etc.)
    - Best-effort JSON repair of response content (like shim)
    - Return in OpenAI ChatCompletion-compatible SimpleNamespace format
    """

    # (A) Remove keys that cause 400 in HCX
    kwargs.pop(
        "response_format", None
    )  # Avoid 'Invalid parameter: response_format.type'
    kwargs.pop("stream", None)
    for k in (
        "response_model",
        "max_retries",
        "validation_context",
        "tool_choice",
        "parallel_tool_calls",
        "max_completion_tokens",
    ):
        kwargs.pop(k, None)

    run_id = kwargs.pop("_run_id", None)
    debug = bool(kwargs.pop("_debug", False))

    attempt_no = next_attempt(run_id) if debug else 1

    if debug and run_id:
        from .utils import log_replay

        log_replay.info(
            f"[{run_id}] attempt={attempt_no} ▶ RAW INPUT\n{messages_to_text(messages)}"
        )

    client = _get_openai_client(api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )

    # (B) Extract message.content (both SDK object and dictionary)
    try:
        msg_content = completion.choices[0].message.content
    except Exception:
        msg_content = completion["choices"][0]["message"]["content"]

    raw = _extract_text_from_openai_content(msg_content)
    repaired = _parse_json_with_rebuild(raw)
    content = repaired if repaired is not None else raw

    # (C) Extract usage
    pt = ct = None
    try:
        usage = completion.usage or None
        pt = getattr(usage, "prompt_tokens", None)
        ct = getattr(usage, "completion_tokens", None)
    except Exception:
        try:
            usage = completion.get("usage", {}) or {}
            pt = usage.get("prompt_tokens")
            ct = usage.get("completion_tokens")
        except Exception:
            pass

    usage_ns = SimpleNamespace(
        prompt_tokens=pt,
        completion_tokens=ct,
        total_tokens=(
            (pt or 0) + (ct or 0) if (pt is not None or ct is not None) else None
        ),
    )

    if debug and run_id:
        from .utils import log_replay

        log_replay.info(
            f"[{run_id}] attempt={attempt_no} ◀ OUTPUT\n{pretty_json(content)}"
        )

    # (D) Return in OpenAI ChatCompletion-compatible SimpleNamespace format
    #     → instructor.patch can consume it directly
    return SimpleNamespace(
        id=getattr(completion, "id", None)
        or getattr(completion, "get", lambda *_: None)("id"),
        object="chat.completion",
        choices=[
            SimpleNamespace(
                index=0,
                finish_reason="stop",
                message=SimpleNamespace(role="assistant", content=content),
            )
        ],
        usage=usage_ns,
    )
