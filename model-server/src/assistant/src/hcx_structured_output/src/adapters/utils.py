# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/adapters/utils.py
import json
import logging
import re
from collections import defaultdict
from typing import Any, Dict, List, Literal, Optional, Union

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel

log_replay = logging.getLogger("hcx.replay")
_ATTEMPTS: Dict[str, int] = defaultdict(int)


def _get_model_name_fallback(client):
    for k in ("model", "model_name"):
        v = getattr(client, k, None)
        if isinstance(v, str) and v:
            return v
    mk = getattr(client, "model_kwargs", {}) or {}
    for k in ("model", "model_name"):
        v = mk.get(k)
        if isinstance(v, str) and v:
            return v
    return None


def next_attempt(run_id: Optional[str]) -> int:
    if not run_id:
        return 0
    _ATTEMPTS[run_id] += 1
    return _ATTEMPTS[run_id]


def _extract_text_from_blocks(blocks: List[dict]) -> str:
    parts: List[str] = []
    for b in blocks:
        if isinstance(b, dict) and b.get("type") == "text":
            parts.append(str(b.get("text", "")))
    return "\n".join(p for p in parts if p)


def content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        t = content.get("text")
        return str(t) if t is not None else str(content)
    if isinstance(content, list):
        return _extract_text_from_blocks(content)
    return str(content)


def messages_to_text(messages: List[dict], show_roles: bool = True) -> str:
    """
    All messages(system/fewshot/user/assistant) are combined into a readable text.
    Multimodal content is converted into text by collecting text blocks.
    """
    lines: List[str] = []
    for m in messages or []:
        role = (m.get("role") or "").lower()
        text = content_to_text(m.get("content"))
        if show_roles:
            lines.append(f"[{role}]")
        lines.append(text)
        lines.append("---")
    if lines and lines[-1] == "---":
        lines.pop()
    return "\n".join(lines)


def pretty_json(text: str, max_len: int = 4000) -> str:
    s = text or ""
    try:
        obj = json.loads(s)
        s = json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        pass
    if len(s) > max_len:
        return s[:max_len] + " …(truncated)"
    return s


def log_attempt_io(
    run_id: Optional[str],
    attempt_no: int,
    messages: List[dict],
    output_text: str,
    *,
    label: str = "RAW INPUT",
    show_roles: bool = True,
) -> None:
    """
    Log both the entire input(messages) block and the output(JSON pretty).
    RAW/EFFECTIVE can be distinguished by label.
    """
    if not run_id:
        return
    inp = messages_to_text(messages, show_roles=show_roles)
    if inp:
        log_replay.info(f"[{run_id}] attempt={attempt_no} ▶ {label}\n{inp}")
    log_replay.info(
        f"[{run_id}] attempt={attempt_no} ◀ OUTPUT\n{pretty_json(output_text)}"
    )


def _tool_choice_hint(
    tool_choice: Optional[
        Union[dict, str, Literal["auto", "none", "required", "any"], bool]
    ],
    tool_names: list[str],
) -> str:
    str_default_set_tool = "필요한 경우에만 적절한 도구를 선택하세요."
    if tool_choice in (None, False, "auto"):
        return str_default_set_tool
    if tool_choice == "none":
        return None
    if tool_choice in (True, "required", "any"):
        return "반드시 하나 이상의 도구를 호출해야 합니다."
    if isinstance(tool_choice, str):
        if tool_choice in tool_names:
            return f'반드시 "{tool_choice}" 라는 이름의 도구를 호출해야 합니다.'
        return str_default_set_tool
    if isinstance(tool_choice, dict):
        name = tool_choice.get("function", {}).get("name")
        if name in tool_names:
            return f'반드시 "{tool_choice}" 라는 이름의 도구를 호출해야 합니다.'
        return str_default_set_tool
    return str_default_set_tool


_PRIMITIVE_MAP: Dict[str, str] = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
}


def _json_field_to_spec(field_schema: Dict[str, Any], required: bool) -> Any:
    """Convert a (subset of) JSON Schema field to a spec string for build_model_from_spec."""
    enum_vals = field_schema.get("enum")
    if isinstance(enum_vals, list):
        spec: Any = {"enum": enum_vals}
        if not required:
            spec["required"] = False
        return spec

    if "anyOf" in field_schema:
        non_null = [s for s in field_schema["anyOf"] if s.get("type") != "null"]
        if len(non_null) == 1:
            inner_spec = _json_field_to_spec(non_null[0], required=True)
            if isinstance(inner_spec, str):
                return f"Optional[{inner_spec}]"
            return {"type": inner_spec, "required": False}
        return "Any"

    t = field_schema.get("type")

    if t == "array":
        items = field_schema.get("items") or {}
        inner_type = _PRIMITIVE_MAP.get(items.get("type", ""), "str")
        spec = f"List[{inner_type}]"
    elif t == "object":
        if "additionalProperties" in field_schema:
            inner = _json_field_to_spec(
                field_schema["additionalProperties"], required=True
            )
            if isinstance(inner, str) and inner.startswith("List["):
                spec = f"dict[str, {inner}]"
            else:
                spec = "dict"
        else:
            spec = "dict"
    else:
        spec = _PRIMITIVE_MAP.get(t, "str")

    if not required:
        if isinstance(spec, str):
            return f"Optional[{spec}]"
        return {"type": spec, "required": False}
    return spec


def has_image_url(messages: list[BaseMessage]) -> bool:
    """
    Check if any HumanMessage (or other BaseMessage) in the list
    contains an image_url content block.
    """
    for msg in messages:
        if isinstance(msg.content, list):
            for block in msg.content:
                if isinstance(block, dict) and block.get("type") in [
                    "image_url",
                    "image",
                ]:
                    return True
    return False


def detect_tool_call(content: str) -> Union[dict, str]:
    """
    Determine whether the model's output is a tool-calling JSON or a plain text response.
    - If it's valid JSON, return a dict ({"calls": [...]})
    - If it's plain text, return the original string
    - Name normalization: "calls" item contains dicts mixed with strings, which causes errors (unhashable) or failure to extract names in subsequent steps.
      -> each item is normalized to a string tool name, and always returns {"calls": [<str>, ...]} form.
    """

    if not content or not isinstance(content, str):
        return content
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return content

    if not isinstance(parsed, dict) or "calls" not in parsed:
        return content

    calls_raw = parsed["calls"]
    raw_list = calls_raw if isinstance(calls_raw, list) else [calls_raw]

    def _name(x):
        if isinstance(x, str):
            return x.strip() or None
        if isinstance(x, dict):
            # support {"name": "..."} / {"tool_name": "..."}
            for key in ("name", "tool_name"):
                val = x.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
            # support single item: {"function":{"name":"..."}}
            fn = x.get("function")
            if isinstance(fn, dict):
                val = fn.get("name")
                if isinstance(val, str) and val.strip():
                    return val.strip()
        return None

    # duplicate removal is optional, but applied for safety
    seen, calls = set(), []
    for item in raw_list:
        n = _name(item)
        if n and n not in seen:
            seen.add(n)
            calls.append(n)

    return {"calls": calls} if calls else content


def tool_json_schema(tool: BaseTool) -> Dict[str, Any]:
    if getattr(tool, "args_schema", None) is not None:
        model = tool.args_schema
        # pydantic v2
        if hasattr(model, "model_json_schema"):
            schema = model.model_json_schema()
        # pydantic v1
        elif hasattr(model, "schema"):
            schema = model.schema()
        else:
            schema = {}

        if tool.description:
            schema["description"] = tool.description
        return schema
    return {}


def _json_type_token(fsch: Dict[str, Any]) -> str:
    variants = fsch.get("anyOf") or fsch.get("oneOf")
    if variants:
        base = next(
            (v for v in variants if isinstance(v, dict) and v.get("type") != "null"), {}
        )
        return _json_type_token(base)

    t = fsch.get("type")
    if t == "boolean":
        return "bool"
    if t == "integer":
        return "int"
    if t == "number":
        return "float"
    if t == "string":
        return "str"
    if t == "array":
        item = fsch.get("items", {})
        return f"List[{_json_type_token(item)}]"
    if t == "object":
        return "dict"
    if "$ref" in fsch:
        return "dict"
    return "any"


def json_schema_to_build_spec(parameters_schema: Dict[str, Any]) -> Dict[str, Any]:
    """OpenAI-style parameters JSON Schema → build_model_from_spec"""
    props = parameters_schema.get("properties", {}) or {}
    spec: Dict[str, Any] = {}
    required_list = set(parameters_schema.get("required", []) or [])
    for name, fsch in props.items():
        spec[name] = _json_field_to_spec(fsch, required=(name in required_list))
    return spec


def _user_provided_pmodel(tool):
    p = getattr(tool, "args_schema", None)
    if isinstance(p, type) and issubclass(p, BaseModel):
        if not getattr(p, "__module__", "").startswith("langchain_core.utils.pydantic"):
            return p
    return None


def extract_tools_schemas(tools: List[BaseTool]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for t in tools:
        name = getattr(t, "name", None) or t.__class__.__name__
        pmodel = _user_provided_pmodel(t)
        if pmodel:
            js = (
                pmodel.model_json_schema()
                if hasattr(pmodel, "model_json_schema")
                else pmodel.schema()
            )
            out[name] = {
                "pydantic_model": pmodel,  # directly store Pydantic model
                "properties": json_schema_to_build_spec(js) if js else {},
            }
        else:
            js = tool_json_schema(t)
            out[name] = {
                "title": js.get("title", name) if js else name,
                "description": js.get("description", "") if js else "",
                "json_schema": js,
                "pydantic_model": None,
                "properties": json_schema_to_build_spec(js) if js else {},
            }
    return out


def parse_tool_message(
    messages: Union[BaseMessage, List[BaseMessage]],
    default_system_prompt: Optional[SystemMessage],
) -> List[Union[SystemMessage, HumanMessage]]:
    """
    Parse BaseMessage list (or single message), filtering only ToolMessage.
    Extracts [SYSTEM], [USER], [REFERENCE] blocks.
    - If multiple [SYSTEM] blocks exist in one ToolMessage,
      replace with default_system_prompt.
    """
    # 리스트로 normalize
    if not isinstance(messages, list):
        messages = [messages]

    # ToolMessage만 필터링
    tool_messages = list(
        {m.content: m for m in messages if isinstance(m, ToolMessage)}.values()
    )

    parsed: List[Union[SystemMessage, HumanMessage]] = []
    reference_contents = []
    sections = []

    for msg in tool_messages:
        text = str(msg.content)
        sys_content = ""
        user_content = ""

        if "[REFERENCE]" in text:
            text, ref_part = text.split("[REFERENCE]", 1)
            reference_content = ref_part.strip()
            reference_contents.append(reference_content)

        sections = text.split("[SYSTEM]")

        if len(sections) > 1:
            sys_part = sections[1]
            if "[USER]" in sys_part:
                sys_content, user_part = sys_part.split("[USER]", 1)
                sys_content = sys_content.strip()
                user_content = user_part.strip()
            else:
                sys_content = sys_part.strip()

            if sys_content:
                if reference_contents:
                    ref_str = "\n".join(reference_contents)
                    sys_content = f"{sys_content}\n\n{ref_str}"
                parsed.append(SystemMessage(content=sys_content))
            if user_content:
                parsed.append(HumanMessage(content=user_content.strip()))
        else:
            # not system, only user
            if "[USER]" in text:
                _, user_part = text.split("[USER]", 1)
                user_content = user_part.strip()
                if user_content:
                    parsed.append(HumanMessage(content=user_content))

    if len([m for m in parsed if isinstance(m, SystemMessage)]) > 1:
        # SystemMessage가 2개 이상 → default_prompt
        parsed = []
        sys_content = default_system_prompt.content
        if reference_contents:
            ref_str = "\n".join(reference_contents)
            sys_content = f"{sys_content}\n{ref_str}"
        parsed = [SystemMessage(content=sys_content)]
    return parsed


def merge_and_filter_messages(
    messages: List[BaseMessage], tool_messages: List[BaseMessage]
) -> List[BaseMessage]:
    """
    Merge tool_messages and messages with filtering rules:
    1. Remove ToolMessage from `messages`
    2. Remove AIMessage with empty content
    3. Merge tool messages + filtered_messages
    """
    # filter out ToolMessage and empty AIMessage
    filtered_messages = [
        ms
        for ms in messages
        if not isinstance(ms, ToolMessage)
        and not (isinstance(ms, AIMessage) and not ms.content)
    ]
    if tool_messages:
        if isinstance(tool_messages[-1], HumanMessage):
            for msg in reversed(filtered_messages):
                if isinstance(msg, HumanMessage):
                    if isinstance(msg.content, list):
                        image_items = [
                            item
                            for item in msg.content
                            if item.get("type") == "image_url"
                        ]
                        if image_items:
                            if isinstance(tool_messages[-1].content, str):
                                tool_messages[-1].content = [
                                    {
                                        "type": "text",
                                        "text": str(tool_messages[-1].content),
                                    }
                                ]
                            tool_messages[-1].content.extend(image_items)
                break
            return tool_messages
        else:
            return tool_messages + filtered_messages
    else:
        return filtered_messages


def normalize_parts_image(parts: list) -> list:
    norm = []
    for p in parts:
        if not isinstance(p, dict):
            continue
        t = p.get("type")
        if t == "image":
            url = p.get("content") or p.get("url")
            if url:
                norm.append({"type": "image_url", "image_url": {"url": url}})
        elif t == "image_url":
            if (
                "image_url" in p
                and isinstance(p["image_url"], dict)
                and "url" in p["image_url"]
            ):
                norm.append(p)
            elif "url" in p:
                norm.append({"type": "image_url", "image_url": {"url": p["url"]}})
        elif t == "text":
            text_content = p.get("text") or p.get("content") or ""
            if text_content:
                norm.append({"type": "text", "text": text_content})
    return norm


def build_condensed_conversation(msg_list):
    """SystemMessage를 유지하고, Human/AI 메시지를 하나로 합친 뒤 마지막 이미지 URL을 포함한 리스트 반환"""
    system_msg = None
    text_blocks = []
    image_urls = []

    for m in msg_list:
        if isinstance(m, SystemMessage):
            system_msg = m

        elif isinstance(m, HumanMessage):
            if isinstance(m.content, list):
                for block in m.content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_blocks.append(
                                f"사용자: {block.get('text', '').strip()}"
                            )
                        elif block.get("type") == "image_url":
                            url = block.get("image_url")
                            if isinstance(url, dict):
                                url = url.get("url")
                            image_urls.append(url)
            elif isinstance(m.content, str):
                text_blocks.append(f"사용자: {m.content.strip()}")

        elif isinstance(m, AIMessage):
            if isinstance(m.content, str):
                if isinstance(m.content, str) and "[SYSTEM]" not in m.content:
                    text_blocks.append(f"어시스턴트: {m.content.strip()}")

    combined_text = "<대화>\n" + "\n".join(text_blocks).strip()

    content_list = []
    if image_urls:
        content_list.append({"type": "image_url", "image_url": {"url": image_urls[-1]}})

    content_list.append({"type": "text", "text": combined_text})

    human_msg = HumanMessage(content=content_list)

    return [system_msg, human_msg] if system_msg else [human_msg]
