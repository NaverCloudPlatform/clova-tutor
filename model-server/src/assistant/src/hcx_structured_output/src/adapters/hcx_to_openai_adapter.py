# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/adapters/hcx_to_openai_adapter.py
import json
import re
from collections import defaultdict
from types import SimpleNamespace
from typing import Any, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_naver import ChatClovaX

from ..utils.load_utils import load_api_config
from .utils import _get_model_name_fallback, messages_to_text, next_attempt, pretty_json

# {key:value} format 단일 field json 객체 검사후 key, value 추출
_SINGLE_FIELD_OBJ = re.compile(
    r'^\s*\{\s*"(?P<key>[^"]+)"\s*:\s*"(?P<val>[\s\S]*)"\s*\}\s*$',
    re.DOTALL,
)

_LAST_RAW_BY_RUN_ID = {}
_ATTEMPTS_BY_RUN_ID = defaultdict(list)


def pop_attempts_and_last(run_id: str):
    attempts = _ATTEMPTS_BY_RUN_ID.pop(run_id, [])
    last = _LAST_RAW_BY_RUN_ID.pop(run_id, None)
    return attempts, last


def _rebuild_single_field_json(text: str) -> Optional[str]:
    m = _SINGLE_FIELD_OBJ.match(text)
    if not m:
        return None
    key = m.group("key")
    raw_val = m.group("val")
    try:
        val = json.loads(f'"{raw_val}"')
    except Exception:
        return None
    return json.dumps({key: val}, ensure_ascii=False)


def to_lc_message(role: str, content: Any):
    """
    Convert role and content to LangChain message object from OpenAI format
    """
    r = (role or "user").lower()
    if r == "system":
        return SystemMessage(content=content)
    if r == "assistant":
        return AIMessage(content=content)
    return HumanMessage(content=content)


def _extract_text_from_clova(ai_msg: Any) -> str:
    raw = getattr(ai_msg, "content", "")
    if isinstance(raw, list):
        text_parts = [
            str(b.get("text", ""))
            for b in raw
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        return "\n".join(t for t in text_parts if t)
    elif isinstance(raw, dict):
        return json.dumps(raw, ensure_ascii=False)
    else:
        return str(raw)


def _parse_json_with_rebuild(content: str) -> Optional[str]:
    """
    Clova response text to best-effort 'JSON object' string.
    - return cleaned JSON string if success
    - return None if failed (no exception) → Instructor can detect parsing/validation failure and re-ask loop
    """
    cleaned = (content or "").strip()

    # 코드펜스 제거
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()

    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return json.dumps(obj, ensure_ascii=False)
    except Exception:
        pass

    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        try:
            unwrapped = json.loads(cleaned)  # 1st unwrap -> expect string
            if isinstance(unwrapped, str):
                obj2 = json.loads(unwrapped)  # 2nd parse -> JSON
                if isinstance(obj2, dict):
                    return json.dumps(obj2, ensure_ascii=False)
        except Exception:
            pass

    # 3) rebuild single field object: {"key":"..."} → {"key": "..."} (escape normalization)
    rebuilt = _rebuild_single_field_json(cleaned)
    if rebuilt:
        try:
            obj3 = json.loads(rebuilt)
            if isinstance(obj3, dict):
                return json.dumps(obj3, ensure_ascii=False)
        except Exception:
            pass

    return None


def clovax_chat_completions_create(
    *,
    messages: List[dict],
    existing_client: Optional[Any] = None,
    **kwargs,
) -> Any:
    # Instructor internal keys are not allowed to flow to Clova API
    for k in ("response_model", "max_retries", "validation_context", "stream"):
        kwargs.pop(k, None)
    # Remove parameters not compatible with Clova
    kwargs.pop("max_completion_tokens", None)

    run_id = kwargs.pop("_run_id", None)
    debug = bool(kwargs.pop("_debug", False))

    attempt_no = next_attempt(run_id) if debug else 1

    if debug and run_id:
        from .utils import log_replay

        log_replay.info(
            f"[{run_id}] attempt={attempt_no} ▶ RAW INPUT\n{messages_to_text(messages)}"
        )

    lc_msgs = [to_lc_message(m["role"], m["content"]) for m in messages]

    # 기존 클라이언트가 있으면 사용, 없으면 새로 생성
    if existing_client:
        client = existing_client
    else:
        # API key와 model을 kwargs에서 가져와서 새 클라이언트 생성
        api_key = kwargs.pop("api_key", None)
        model = kwargs.pop("model", "HCX-005")
        if not api_key:

            config = load_api_config()
            api_key = config[model.lower()]["api_key"]
        client = ChatClovaX(model=model, api_key=api_key)

    # double attempt based on response_format presence (compatibility ↑)
    attempt_kwargs_list: List[dict] = [dict(kwargs)]
    if "response_format" in kwargs:
        cleaned = dict(kwargs)
        cleaned.pop("response_format", None)
        attempt_kwargs_list.append(cleaned)

    ai_msg = None
    last_err: Optional[Exception] = None
    for attempt_kwargs in attempt_kwargs_list:
        try:
            ai_msg = client.invoke(lc_msgs, **attempt_kwargs)
            break
        except Exception as e:
            last_err = e
            continue
    if ai_msg is None:
        raise last_err or RuntimeError("ChatClovaX.invoke failed")

    raw = _extract_text_from_clova(ai_msg)

    # best-effort JSON repair: return cleaned JSON string if success, otherwise return original text
    repaired = _parse_json_with_rebuild(raw)
    content = repaired if repaired is not None else raw

    # extract usage metadata
    usage_md = getattr(ai_msg, "response_metadata", {}) or {}
    token_usage = usage_md.get("token_usage") or {}
    pt = token_usage.get("prompt_tokens") or usage_md.get("prompt_tokens")
    ct = token_usage.get("completion_tokens") or usage_md.get("completion_tokens")
    usage = SimpleNamespace(
        prompt_tokens=pt,
        completion_tokens=ct,
        total_tokens=(
            (pt or 0) + (ct or 0) if (pt is not None or ct is not None) else None
        ),
        # OpenAI compatible aliases
        input_tokens=pt,
        output_tokens=ct,
    )

    if debug and run_id:
        from .utils import log_replay

        log_replay.info(
            f"[{run_id}] attempt={attempt_no} ◀ OUTPUT\n{pretty_json(content)}"
        )

    chat_completion = SimpleNamespace(
        id="chatcmpl-clovax-shim",
        object="chat.completion",
        choices=[
            SimpleNamespace(
                index=0,
                finish_reason="stop",
                message=SimpleNamespace(role="assistant", content=content),
            )
        ],
        usage=usage,
        model_name=_get_model_name_fallback(client),
    )

    if run_id:
        _LAST_RAW_BY_RUN_ID[run_id] = chat_completion
        _ATTEMPTS_BY_RUN_ID[run_id].append(chat_completion)

    return chat_completion
