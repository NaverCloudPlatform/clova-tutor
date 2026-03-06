# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/utils/runner.py
import logging
import uuid
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional

import instructor
from instructor.exceptions import InstructorRetryException
from langchain_core.messages import AIMessage
from pydantic import BaseModel

from ..adapters.hcx_to_openai_adapter import (
    clovax_chat_completions_create,
    pop_attempts_and_last,
)
from ..adapters.hcx_using_openai_client import safe_openai_create
from .chunk import split_text
from .constants import DEFAULT_MAX_RETRIES, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from .merge import merge_pydantic_models
from .reask import manual_retry_loop

_CreateFn = Callable[..., Any]
_CREATE_JSON_CACHE: Dict[str, _CreateFn] = {}


class StructuredRunnable:
    def __init__(self, response_model, run_kwargs):
        self.response_model = response_model
        self.run_kwargs = run_kwargs

    def invoke(self, user_input):
        return run_structured_task(
            response_model=self.response_model,
            user_content=user_input,
            **self.run_kwargs,
        )


def with_structured_output_like(response_model, **run_kwargs):
    return StructuredRunnable(response_model, run_kwargs)


def _get_patched_create(
    backend: Literal["langchain", "openai"] = "langchain",
    existing_client: Optional[Any] = None,
) -> _CreateFn:
    """
    Return instructor.patch(create=...) once per backend.
    - "langchain": langchain_naver.ChatClovaX path
    - "openai":    HCX OpenAI-compatible endpoint path
    """
    # 기존 클라이언트가 있으면 별도 키로 캐시
    key = f"{backend}_{id(existing_client) if existing_client else 'default'}"
    if key in _CREATE_JSON_CACHE:
        return _CREATE_JSON_CACHE[key]

    if existing_client and backend == "langchain":
        # 기존 클라이언트를 사용하는 커스텀 create 함수
        def custom_create_with_client(**kwargs):
            return clovax_chat_completions_create(
                existing_client=existing_client, **kwargs
            )

        base_create = custom_create_with_client
    else:
        base_create = (
            safe_openai_create
            if backend == "openai"
            else clovax_chat_completions_create
        )

    patched = instructor.patch(create=base_create, mode=instructor.Mode.JSON)
    _CREATE_JSON_CACHE[key] = patched
    return patched


def _as_user_message(user_content: Any) -> dict:
    if isinstance(user_content, dict) and user_content.get("role"):
        return user_content
    if isinstance(user_content, (list, tuple)):
        return {"role": "user", "content": list(user_content)}
    return {"role": "user", "content": user_content}


def _make_messages(
    system_rules: str, fewshots: List[dict], user_msg: dict
) -> List[dict]:
    return [{"role": "system", "content": system_rules}] + (fewshots or []) + [user_msg]


def handle_instructor_retry(default_return=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (InstructorRetryException, Exception) as e:
                # TODO: Change logger and return {parsed: None}
                print(f"[InstructorRetryException] {e}")
                return default_return

        return wrapper

    return decorator


@handle_instructor_retry(default_return=None)
def run_structured_task(
    *,
    system_rules: str,
    fewshots: List[dict],
    user_content: Any,
    response_model: type[BaseModel],
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_retries: int = DEFAULT_MAX_RETRIES,
    chunk_policy: Optional[Dict[str, Any]] = None,
    backend: Literal["langchain", "openai"] = "langchain",
    debug: bool = False,
    retry_mode: Literal["manual", "instructor"] = "manual",
    language: str = "ko",
    existing_client: Optional[Any] = None,  # 기존 클라이언트 인스턴스
    include_raw: bool = False,
):
    if debug and not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        logging.getLogger("instructor").setLevel(logging.DEBUG)

    _create_json = _get_patched_create(backend, existing_client)
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    parsing_error = None
    parsed = None

    def _call_with_retry(base_messages: List[dict]) -> BaseModel:
        if retry_mode == "instructor":
            return _create_json(
                model=model,
                messages=base_messages,
                temperature=temperature,
                response_model=response_model,
                max_retries=max_retries,
                _run_id=run_id,
                _debug=debug,
            )
        return manual_retry_loop(
            _create_json,
            model=model,
            base_messages=base_messages,
            temperature=temperature,
            response_model=response_model,
            max_retries=max_retries,
            run_id=run_id,
            debug=debug,
            language=language,
        )

    def _wrap_return():
        if not include_raw:
            return parsed
        attempts, chat_completion = pop_attempts_and_last(run_id)

        def _u(a, k):
            u = getattr(a, "usage", None)
            return getattr(u, k, 0) or 0

        prompt_sum = sum(_u(a, "input_tokens") for a in attempts)
        completion_sum = sum(_u(a, "output_tokens") for a in attempts)
        total_sum = sum(_u(a, "total_tokens") for a in attempts) or (
            prompt_sum + completion_sum
        )

        token_usage_last = {}
        if chat_completion and getattr(chat_completion, "usage", None):
            token_usage_last = {
                "input_tokens": getattr(chat_completion.usage, "input_tokens", None),
                "output_tokens": getattr(chat_completion.usage, "output_tokens", None),
                "total_tokens": getattr(chat_completion.usage, "total_tokens", None),
            }
        raw_msg = AIMessage(
            content=(
                chat_completion.choices[0].message.content if chat_completion else ""
            ),
            response_metadata={
                "token_usage": token_usage_last,  # 마지막 응답에 대한 값
                "token_usage_total": {  # 모든 시도 누계 (max_retry 고려)
                    "input_tokens": prompt_sum,
                    "output_tokens": completion_sum,
                    "total_tokens": total_sum,
                },
                "attempts": len(attempts),
                "model_name": (
                    getattr(chat_completion, "model_name", None)
                    if chat_completion
                    else None
                ),
            },
        )

        return {
            "raw": raw_msg,
            "parsed": parsed,
            "parsing_error": parsing_error,
        }

    # 1) no-chunk
    if not chunk_policy:
        user_msg = _as_user_message(user_content)
        messages = _make_messages(system_rules, fewshots, user_msg)
        parsed = _call_with_retry(messages).model_dump()
        return _wrap_return()

    # 2) chunk
    source_text = chunk_policy["source_text"]
    max_chars = int(chunk_policy.get("max_chars", 400))
    pre = chunk_policy.get("pre_prompt", "")
    post = chunk_policy.get("post_prompt", "")

    parts = split_text(source_text, max_chars=max_chars)
    partials: List[BaseModel] = []

    base_user = _as_user_message(user_content)
    for i, part in enumerate(parts, 1):
        chunk_text = f"{pre}{part}{post}"

        if isinstance(base_user.get("content"), list):
            new_blocks = []
            inserted = False
            for block in base_user["content"]:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "text"
                    and not inserted
                ):
                    prev = str(block.get("text", ""))
                    sep = "\n" if prev else ""
                    new_blocks.append({"type": "text", "text": prev + sep + chunk_text})
                    inserted = True
                else:
                    new_blocks.append(block)
            if not inserted:
                new_blocks = [{"type": "text", "text": chunk_text}] + new_blocks
            user_msg = {"role": "user", "content": new_blocks}
        else:
            prev = str(base_user.get("content", ""))
            sep = "\n" if prev else ""
            user_msg = {"role": "user", "content": prev + sep + chunk_text}

        messages = _make_messages(system_rules, fewshots, user_msg)
        partial = _call_with_retry(messages)
        partials.append(partial)

    parsed = merge_pydantic_models(partials, response_model).model_dump()
    return _wrap_return()
