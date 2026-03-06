# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/adapters/clovax_hso.py
import uuid
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
)

import openai
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import generate_from_stream
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_naver import ChatClovaX
from langchain_naver.chat_models import _convert_payload_messages
from langchain_openai.chat_models.base import (
    _DictOrPydantic,
    _DictOrPydanticClass,
    _handle_openai_bad_request,
)
from pydantic import BaseModel, Field

from ..schemas import build_model_from_spec
from ..utils import load_prompt_yaml
from ..utils.load_utils import load_api_config
from ..utils.runner import run_structured_task
from .utils import (
    _tool_choice_hint,
    build_condensed_conversation,
    detect_tool_call,
    extract_tools_schemas,
    has_image_url,
    merge_and_filter_messages,
    normalize_parts_image,
    parse_tool_message,
)


def _last_human_content(messages: List[BaseMessage]):
    last_human = None
    for m in messages:
        if isinstance(m, HumanMessage):
            last_human = m
    if last_human is not None:
        return last_human.content  # can be str or list[dict] (text/image_url blocks)
    return messages[-1].content if messages else ""


def _extract_model_name(self, override: Optional[str] = None) -> str:
    if override:
        return override
    for attr in ("model", "model_name"):
        v = getattr(self, attr, None)
        if isinstance(v, str) and v:
            return v
    try:
        for k in ("model", "model_name"):
            v = self.__dict__.get(k)
            if isinstance(v, str) and v:
                return v
    except Exception:
        pass
    mk = getattr(self, "model_kwargs", {}) or {}
    v = mk.get("model") or mk.get("model_name")
    if isinstance(v, str) and v:
        return v
    raise RuntimeError(
        "Cannot determine model name. Pass `model_for_fallback` explicitly."
    )


class PromptToolMessageBundle(BaseModel):
    system: Optional[str] = None
    user: Optional[str] = None
    reference: Optional[str] = None

    def __str__(self):
        parts = []
        if self.system:
            parts.append(f"[SYSTEM]\n{self.system}")
        if self.user:
            parts.append(f"[USER]\n{self.user}")
        if self.reference:
            parts.append(f"[REFERENCE]\n{self.reference}")
        return "\n\n".join(parts)


@dataclass(frozen=True)
class FallbackConfig:
    system_rules: str = ""
    fewshots: List[dict] | None = None
    model: str = "hcx-005"
    temperature: float = 0.01
    max_retries: int = 10
    backend: str = "langchain"  # use instructor patched adapter
    retry_mode: str = "manual"  # or "manual"
    language: str = "ko"
    debug: bool = False
    existing_client: Optional[Any] = None  # 기존 클라이언트 인스턴스

    def to_kwargs(self) -> Dict[str, Any]:
        return dict(
            system_rules=self.system_rules,
            fewshots=self.fewshots or [],
            model=self.model,
            temperature=self.temperature,
            max_retries=self.max_retries,
            backend=self.backend,
            retry_mode=self.retry_mode,
            language=self.language,
            debug=self.debug,
        )


class _FallbackRunnable(Runnable):
    """use run_structured_task to generate structured output."""

    def __init__(self, schema: type[BaseModel], cfg: FallbackConfig, include_raw: bool):
        self.schema = schema
        self.cfg = cfg
        self.include_raw = include_raw

    async def ainvoke(self, query_input: Any, **kwargs):
        # TODO: implement async version (needs to be tested)
        return self.invoke(query_input, **kwargs)

    def invoke(self, query_input: Any, **kwargs):
        # 기존 클라이언트가 있으면 전달
        run_kwargs = self.cfg.to_kwargs()
        if self.cfg.existing_client:
            run_kwargs["existing_client"] = self.cfg.existing_client
        if isinstance(query_input, list) and all(
            isinstance(m, BaseMessage) for m in query_input
        ):
            user_content = _last_human_content(query_input)
        else:
            user_content = query_input

        result = run_structured_task(
            response_model=self.schema,
            user_content=user_content,
            include_raw=self.include_raw,
            **run_kwargs,
        )

        # Accumulate token usage to existing_client if available
        if self.cfg.existing_client and isinstance(result, dict) and "raw" in result:
            raw_metadata = result["raw"].response_metadata
            token_usage_total = raw_metadata.get("token_usage_total", {})
            attempts_count = raw_metadata.get("attempts", 0)

            # Update token counters on the ChatClovaXHSO instance
            self.cfg.existing_client.hso_input_tokens += token_usage_total.get(
                "input_tokens", 0
            )
            self.cfg.existing_client.hso_output_tokens += token_usage_total.get(
                "output_tokens", 0
            )
            self.cfg.existing_client.hso_invoke_count += 1
            self.cfg.existing_client.hso_attempt_count += attempts_count

        if self.include_raw:
            return result
        else:
            # Return only parsed data if user didn't request raw
            return result.get("parsed") if isinstance(result, dict) else result

    def batch(self, query_inputs: List[Any], **kwargs):
        """Parallel batch inference over query_inputs using self.invoke()."""
        results = []

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.invoke, q, **kwargs) for q in query_inputs]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(None)
        return results


class ChatClovaXHSO(ChatClovaX):
    """
    ⚠️ HCX(ChatClovaX) has constraints on parallel_tool_calls / JSON mode,
    so LangChain native with_structured_output is not used.

    Always use instructor-based run_structured_task (hso module) fallback.
    """

    HSO_PROMPT: str = Field(default="")
    HSO_FEWSHOTS: list = Field(default_factory=list)
    image_tool_call_msg: str = Field(
        default="위 이미지를 반드시 확인하고 이미지의 내용을 분석하여 반말로 친근하게 응답해."
    )
    default_system_prompt: SystemMessage = Field(
        default="사용자의 응답에 친절하게 답변해야해."
    )

    tool_calls_info: list = Field(default_factory=list)
    tool_calls_tracker: Optional[Callable] = Field(default=None)

    # Token tracking for HSO calls
    hso_input_tokens: int = Field(default=0)
    hso_output_tokens: int = Field(default=0)
    hso_invoke_count: int = Field(default=0)  # Number of invoke() calls
    hso_attempt_count: int = Field(default=0)  # Total attempts including retries

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "HCX-005",
        default_system_str: Optional[str] = None,
        **kwargs,
    ):
        if api_key is None:
            api_key = self._load_api_key(model)

        super().__init__(api_key=api_key, model=model, **kwargs)
        # Use absolute path relative to this file
        prompt_path = Path(__file__).parent.parent / "prompt" / "prompt_generic.yaml"
        self.HSO_PROMPT, self.HSO_FEWSHOTS = load_prompt_yaml(prompt_path)
        self.default_system_prompt = SystemMessage(content=default_system_str)

    def _load_api_key(self, model: str = "HCX-005") -> str:
        config = load_api_config()
        if model.lower() not in config:
            raise KeyError(f"Model {model} not found in api_info.yaml")
        return config[model.lower()]["api_key"]

    def get_hso_token_usage(self) -> dict:
        """Get accumulated HSO token usage."""
        return {
            "input_tokens": self.hso_input_tokens,
            "output_tokens": self.hso_output_tokens,
            "total_tokens": self.hso_input_tokens + self.hso_output_tokens,
            "invoke_count": self.hso_invoke_count,
            "attempt_count": self.hso_attempt_count,
        }

    def reset_hso_token_usage(self) -> None:
        """Reset HSO token usage counters."""
        self.hso_input_tokens = 0
        self.hso_output_tokens = 0
        self.hso_invoke_count = 0
        self.hso_attempt_count = 0

    def _track_tool_calls_if_enabled(
        self, oai_tool_calls: List[Dict[str, Any]]
    ) -> None:
        """Track tool calls for testing purposes if tracker is enabled."""
        if not self.tool_calls_tracker or not oai_tool_calls:
            return

        # Call the tracker function with tool calls
        self.tool_calls_tracker(oai_tool_calls)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            stream_iter = self._stream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)
        # changed_line
        kwargs.pop("final_response_dict", {})
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        _convert_payload_messages(payload)
        extra_headers = {"X-NCP-CLOVASTUDIO-REQUEST-ID": f"lcnv-{str(uuid.uuid4())}"}
        if "response_format" in payload:
            payload.pop("stream")
            payload.pop("response_format")
            try:
                response = self.root_client.beta.chat.completions.parse(
                    **payload,
                    extra_headers=extra_headers,
                )
            except openai.BadRequestError as e:
                _handle_openai_bad_request(e)
        else:
            response = self.client.create(
                **payload,
                extra_headers=extra_headers,
            )
        return self._create_chat_result(response)

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        *,
        stream_usage: Optional[bool] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        kwargs["stream"] = True
        # changed_line
        final_response = kwargs.pop("final_response_dict", {}).copy()
        stream_usage = self._should_stream_usage(stream_usage, **kwargs)
        if stream_usage:
            kwargs["stream_options"] = {"include_usage": stream_usage}
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        default_chunk_class: type[BaseMessageChunk] = AIMessageChunk
        base_generation_info = {}

        if "response_format" in payload:
            if self.include_response_headers:
                warnings.warn(
                    "Cannot currently include response headers when response_format is "
                    "specified."
                )
            payload.pop("stream")
            payload.pop("response_format")
            response_stream = self.root_client.beta.chat.completions.stream(**payload)
            context_manager = response_stream
        else:
            if self.include_response_headers:
                raw_response = self.client.with_raw_response.create(**payload)
                response = raw_response.parse()
                base_generation_info = {"headers": dict(raw_response.headers)}
            else:
                response = self.client.create(**payload)
            context_manager = response
        try:
            with context_manager as response:
                is_first_chunk = True
                for chunk in response:
                    if not isinstance(chunk, dict):
                        chunk = chunk.model_dump()
                    generation_chunk = self._convert_chunk_to_generation_chunk(
                        chunk,
                        default_chunk_class,
                        base_generation_info if is_first_chunk else {},
                    )
                    if generation_chunk is None:
                        continue
                    default_chunk_class = generation_chunk.message.__class__
                    logprobs = (generation_chunk.generation_info or {}).get("logprobs")
                    if run_manager:
                        run_manager.on_llm_new_token(
                            generation_chunk.text,
                            chunk=generation_chunk,
                            logprobs=logprobs,
                        )
                    is_first_chunk = False
                    # changed line
                    if final_response.get("final_response", None):
                        generation_chunk.message.additional_kwargs.update(
                            final_response
                        )
                    yield generation_chunk
        except openai.BadRequestError as e:
            _handle_openai_bad_request(e)
        if hasattr(response, "get_final_completion") and "response_format" in payload:
            final_completion = response.get_final_completion()
            generation_chunk = self._get_generation_chunk_from_completion(
                final_completion
            )
            if run_manager:
                run_manager.on_llm_new_token(
                    generation_chunk.text, chunk=generation_chunk
                )
            yield generation_chunk

    def with_structured_output(
        self,
        schema: Optional[_DictOrPydanticClass] = None,
        *,
        method: Literal[
            "function_calling", "json_mode", "json_schema"
        ] = "function_calling",
        include_raw: bool = True,
        strict: Optional[bool] = None,
        tools: Optional[list] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, _DictOrPydantic]:

        model_name = _extract_model_name(self, kwargs.get("model_for_fallback"))

        cfg = FallbackConfig(
            system_rules=kwargs.get("system_rules", ""),
            fewshots=kwargs.get("fewshots", []),
            model=model_name,
            temperature=kwargs.get("temperature_for_fallback", 0.01),
            max_retries=kwargs.get("max_retries_for_fallback", 10),
            backend=kwargs.get("backend_for_fallback", "langchain"),
            retry_mode=kwargs.get("retry_mode_for_fallback", "manual"),
            language=kwargs.get("language", "ko"),
            debug=kwargs.get("debug", False),
            # 기존 클라이언트 인스턴스 전달
            existing_client=self,
        )
        return _FallbackRunnable(schema, cfg, include_raw)

    def _build_tool_call_tasks(
        self, messages, calls, tool_names, schemas, has_image, max_retries=10
    ):
        """Prepares a list of (i, call_name, structured, messages) for batch processing."""
        tasks = []
        for i, call_name in enumerate(calls):
            if call_name not in tool_names:
                continue
            # args가 없는 도구들은 if calls: ~ 에서도 추가되고, self._build_tool_call_tasks에서도 추가되어 두번 호출됨. 이를 방지하기 위해 아래 조건 추가.
            if not schemas[call_name]["properties"]:
                continue

            meta = schemas[call_name]
            model_cls = meta.get("pydantic_model")
            if model_cls is None:
                build_spec = meta.get("properties")
                model_cls = build_model_from_spec(
                    name=meta.get("title", ""),
                    spec=build_spec,
                    model_description=meta.get("description", ""),
                )

            structured = self.with_structured_output(
                schema=model_cls,  # if args_schema is provided, use Pydantic model directly
                system_rules=self.HSO_PROMPT,
                fewshots=self.HSO_FEWSHOTS,
                max_retries_for_fallback=max_retries,
                debug=False,
                include_raw=True,
            )
            msgs = messages.copy()
            if has_image:
                msgs.append(HumanMessage(content="\n" + self.image_tool_call_msg))
            tasks.append((i, call_name, structured, msgs))
        return tasks

    def _invoke_tool_call_task(self, i, call_name, structured, messages):
        """Invokes a single tool call and returns (success, result_dict)"""
        try:
            raw_response = structured.invoke(messages, method="json_schema")
            if not raw_response:
                return False, None
            args_dict = raw_response["parsed"]
            token_usage_total_tool = raw_response["raw"].response_metadata.get(
                "token_usage_total", {}
            )

            call_id = f"call_{i}-{uuid.uuid4().hex[:8]}"

            return True, {
                "call_id": call_id,
                "call_name": call_name,
                "args_dict": args_dict,
                "token_usage_total_tool": token_usage_total_tool,
            }
        except Exception as e:
            return False, None

    def bind_tools(
        self,
        tools: Sequence[Union[dict[str, Any], type, Callable, BaseTool]],
        *,
        tool_choice: Optional[
            Union[dict, str, Literal["auto", "none", "required", "any"], bool]
        ] = "auto",
        strict: Optional[bool] = None,
        parallel_tool_calls: Optional[bool] = True,
        tag_final_response: Optional[bool] = True,
        max_retries=10,
        max_workers=8,
        tool_select_recursion=False,
        tool_prompt_path: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ) -> Runnable[list[BaseMessage], AIMessage]:
        """
        A binder that enables tool-calling for models without native support,
        by using with_structured_output to parse tool selection into
        OpenAI-style AIMessage(tool_calls=...).

        The `max_retries` parameter defines the maximum number of retries when invoking
        the tool to extract its arguments using a structured output (HSO)-based approach.

        Args:
            tool_prompt_path: Optional path to a custom tool call prompt YAML file.
                If None, checks for instance attribute `tool_prompt_path`, then uses
                the default generic prompt (prompt_tool_call.yaml).
                Can be a string or Path object. If a relative path, it's resolved relative
                to the prompt directory.
        """
        kwargs_final = kwargs.copy()
        if tag_final_response:
            kwargs_final["final_response_dict"] = {"final_response": True}

        # Determine tool prompt path
        if tool_prompt_path is None:
            # Check instance attribute (set by response_react_agent)
            tool_prompt_path = getattr(self, "tool_prompt_path", None)
            if tool_prompt_path is None:
                tool_prompt_path = self.__dict__.get("tool_prompt_path", None)

        if tool_prompt_path is None:
            # Default to generic prompt
            tool_prompt_path = (
                Path(__file__).parent.parent / "prompt" / "prompt_tool_call.yaml"
            )
        else:
            # Convert to Path if string, and resolve relative paths
            tool_prompt_path = Path(tool_prompt_path)
            if not tool_prompt_path.is_absolute():
                # If relative, assume it's relative to the prompt directory
                tool_prompt_path = (
                    Path(__file__).parent.parent / "prompt" / tool_prompt_path
                )

        TOOL_CALL_PROMPT, _ = load_prompt_yaml(tool_prompt_path)
        # extract tool_name and description
        formatted = [convert_to_openai_tool(t, strict=strict) for t in tools]

        tool_names, tool_name_description = zip(
            *(
                (
                    t["function"]["name"],
                    f"- `{t['function']['name']}`: {t['function'].get('description', '').split(chr(10) + chr(10))[0] if t['function'].get('description', '') else ''}",
                )
                for t in formatted
            )
        )
        tool_names = list(tool_names)
        tool_name_description = "\n".join(tool_name_description)

        # extract tool schema and arguments
        schemas = extract_tools_schemas(tools)

        # non-streaming 버전
        def _invoke(messages: list[BaseMessage]) -> AIMessage:
            if tool_choice == "none":
                return self.invoke(messages, **kwargs_final)
            tool_prompt = TOOL_CALL_PROMPT.format(
                tool_list=tool_name_description,
                tool_names=", ".join(f"`{name}`" for name in tool_names),
                tool_choice_hint=_tool_choice_hint(tool_choice, tool_names),
            )

            msgs = [SystemMessage(content=tool_prompt)]
            if isinstance(messages, str):
                msgs.append(HumanMessage(content=[{"type": "text", "text": messages}]))
            elif isinstance(messages, list) and all(
                isinstance(m, BaseMessage) for m in messages
            ):
                new_messages = []
                for m in messages:
                    if isinstance(m, ToolMessage):
                        # TODO: refactoring
                        # tool selection results
                        original_tool_name = getattr(m, "name", None)

                        # Check if same tool was already called in messages history
                        tool_call_history = []
                        for msg in messages:
                            if isinstance(msg, ToolMessage):
                                tool_name = getattr(msg, "name", None)
                                if tool_name:
                                    tool_call_history.append(tool_name)

                        # If same tool was called 2+ times (3rd call), stop and return final answer
                        # Allow 2 calls: 1st call (count=0), 2nd call (count=1), block 3rd call (count>=2)
                        if (
                            original_tool_name
                            and tool_call_history.count(original_tool_name) >= 2
                        ):
                            # if model select same tool
                            tool_message = parse_tool_message(
                                messages,
                                self.default_system_prompt,
                            )
                            filtered_messages = merge_and_filter_messages(
                                messages, tool_message
                            )
                            if tool_message:
                                return self.invoke(filtered_messages, **kwargs_final)
                            else:
                                return self.invoke(
                                    [self.default_system_prompt] + filtered_messages,
                                    **kwargs_final,
                                )

                        m = AIMessage(
                            content=m.content,
                            additional_kwargs={"type": "tool_msg"},
                        )
                    if isinstance(m, HumanMessage):
                        if isinstance(m.content, str):
                            m = HumanMessage(
                                content=[{"type": "text", "text": m.content}],
                                **{
                                    k: v
                                    for k, v in m.__dict__.items()
                                    if k != "content"
                                },
                            )
                        else:
                            normalized_content = normalize_parts_image(m.content)
                            m = HumanMessage(
                                content=normalized_content,
                                **{
                                    k: v
                                    for k, v in m.__dict__.items()
                                    if k != "content"
                                },
                            )
                    if isinstance(m, AIMessage):
                        # sometimes m.content is not str but list type. (to-be fixed)
                        content_str = m.content if isinstance(m.content, str) else ""
                        if not content_str.strip() and m.additional_kwargs.get(
                            "tool_calls"
                        ):
                            continue
                    new_messages.append(m)
                msgs.extend(new_messages)
                has_image = has_image_url(new_messages)
                if has_image:
                    image_prefix = {"type": "text", "text": self.image_tool_call_msg}
                    if isinstance(msgs[-1], HumanMessage):
                        msgs[-1].content.append(image_prefix)
            else:
                raise TypeError(
                    f"messages must be str or list[BaseMessage], got {type(messages)}"
                )

            # first step: extract tool_name or general response
            tool_call_msg = build_condensed_conversation(msgs)
            response = self.invoke(tool_call_msg, **kwargs)
            if not response:
                msgs = [SystemMessage(content=tool_prompt)]
                return self.invoke(messages, **kwargs_final)
            token_usage_total = response.usage_metadata
            parsed = detect_tool_call(response.content)
            calls = parsed.get("calls", []) if isinstance(parsed, dict) else []
            # 도구 목록에 없는 도구는 제거
            calls = [c for c in calls if c in tool_names]

            if not calls:
                if tool_select_recursion:
                    return AIMessage(
                        content="",
                        tool_calls=[],
                        response_metadata={"token_usage": token_usage_total},
                        additional_kwargs={
                            "tool_calls": None,
                            "refusal": None,
                        },
                    )

                tool_messages = parse_tool_message(
                    new_messages, self.default_system_prompt
                )
                # not choose tool and return general response
                if tool_messages:
                    # msg = merge_and_filter_messages(messages, tool_messages)
                    msg = merge_and_filter_messages(new_messages, tool_messages)
                else:
                    # use default prompt
                    # msg = [self.default_system_prompt] + messages
                    msg = [self.default_system_prompt] + new_messages
                return self.invoke(msg, **kwargs_final)

            # second step: extract tool arguments. supports multiple tool calls.
            lc_tool_calls, oai_tool_calls = [], []

            tasks = self._build_tool_call_tasks(
                messages, calls, tool_names, schemas, has_image, max_retries
            )
            # tool에 argument 없을 경우 처리
            if calls:
                for idx, call_name in enumerate(calls):
                    if not schemas[call_name]["properties"]:
                        call_id = call_id = f"call_{idx}-{uuid.uuid4().hex[:8]}"
                        args_dict = {}
                        lc_tool_calls.append(
                            {
                                "name": call_name,
                                "args": args_dict,
                                "id": call_id,
                                "type": "tool_call",
                            }
                        )
                        oai_tool_calls.append(
                            {
                                "id": call_id,
                                "type": "function",
                                "function": {
                                    "name": call_name,
                                    "arguments": args_dict,
                                },
                            }
                        )

            if not parallel_tool_calls:
                tasks = [tasks[0]]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self._invoke_tool_call_task, i, call_name, structured, msgs
                    )
                    for (i, call_name, structured, msgs) in tasks
                ]
                for future in as_completed(futures):
                    success, result = future.result()
                    if not success:
                        continue
                    call_id = result["call_id"]
                    args_dict = result["args_dict"]
                    call_name = result["call_name"]

                    # Merge token usage
                    for k, v in result["token_usage_total_tool"].items():
                        token_usage_total[k] = token_usage_total.get(k, 0) + v

                    # Append to call lists
                    lc_tool_calls.append(
                        {
                            "name": call_name,
                            "args": args_dict,
                            "id": call_id,
                            "type": "tool_call",
                        }
                    )

                    oai_tool_calls.append(
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": call_name,
                                "arguments": args_dict,
                            },
                        }
                    )

            if lc_tool_calls:
                # Debug: Print additional_kwargs content
                additional_kwargs_content = {
                    "tool_calls": oai_tool_calls,
                    "refusal": None,
                }

                # Track tool calls for testing if enabled
                self._track_tool_calls_if_enabled(oai_tool_calls)

                # return results in the same format as OpenAI tool-calling response
                return AIMessage(
                    content="",
                    tool_calls=lc_tool_calls,
                    response_metadata={"token_usage": token_usage_total},
                    additional_kwargs=additional_kwargs_content,
                )
            return self.invoke(messages, **kwargs_final)

        return RunnableLambda(_invoke)
