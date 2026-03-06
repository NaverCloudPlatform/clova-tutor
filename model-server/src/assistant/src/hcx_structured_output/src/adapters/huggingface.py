# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import copy
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from operator import itemgetter
from pathlib import Path
from typing import Any, Callable, Iterator, Literal, Optional, Sequence, Union

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
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
from langchain_core.output_parsers import (
    JsonOutputKeyToolsParser,
    JsonOutputParser,
    PydanticOutputParser,
    PydanticToolsParser,
)
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
)
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import (
    convert_to_json_schema,
    convert_to_openai_tool,
)
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_huggingface import ChatHuggingFace
from langchain_huggingface.chat_models.huggingface import (
    _convert_chunk_to_message_chunk,
    _is_huggingface_endpoint,
    _is_huggingface_textgen_inference,
)
from pydantic import BaseModel, Field
from utils import load_prompt_yaml

from ..utils import (
    _tool_choice_hint,
    detect_tool_call,
    extract_tools_schemas,
    has_image_url,
)


class ChatHuggingFaceWithUsage(ChatHuggingFace):

    stream_usage: bool = False
    """Whether to include usage metadata in streaming output. If True, an additional
    message chunk will be generated during the stream including usage metadata."""
    image_tool_call_msg: str = Field(
        default="사진을 보고 system prompt의 규칙에 따라 JSON 응답을 생성합니다."
    )
    react_qa_msg: str = Field(
        default="도구(tool) 실행 결과를 참조하여 사용자의 질문에 친절하게 응답합니다."
    )
    mimic_tool_msg: str = Field(default="도구(tool) 실행 결과:")

    def _should_stream_usage(
        self, stream_usage: Optional[bool] = None, **kwargs: Any
    ) -> bool:
        """Determine whether to include usage metadata in streaming output.

        For backwards compatibility, we check for `stream_options` passed
        explicitly to kwargs or in the model_kwargs and override self.stream_usage.
        """
        stream_usage_sources = [  # order of precedence
            stream_usage,
            kwargs.get("stream_options", {}).get("include_usage"),
            self.model_kwargs.get("stream_options", {}).get("include_usage"),
            self.stream_usage,
        ]
        for source in stream_usage_sources:
            if isinstance(source, bool):
                return source
        return self.stream_usage

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,  # noqa: FBT001
        **kwargs: Any,
    ) -> ChatResult:
        should_stream = stream if stream is not None else self.streaming

        if _is_huggingface_textgen_inference(self.llm):
            message_dicts, params = self._create_message_dicts(messages, stop)
            answer = self.llm.client.chat(messages=message_dicts, **kwargs)
            return self._create_chat_result(answer)
        if _is_huggingface_endpoint(self.llm):
            if should_stream:
                stream_iter = self._stream(
                    messages, stop=stop, run_manager=run_manager, **kwargs
                )
                return generate_from_stream(stream_iter)
            # changed_line
            kwargs.pop("final_response_dict", {})
            message_dicts, params = self._create_message_dicts(messages, stop)
            params = {
                "stop": stop,
                **params,
                **({"stream": stream} if stream is not None else {}),
                **kwargs,
            }
            answer = self.llm.client.chat_completion(messages=message_dicts, **params)
            return self._create_chat_result(answer)
        llm_input = self._to_chat_prompt(messages)

        if should_stream:
            stream_iter = self.llm._stream(
                llm_input, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)
        llm_result = self.llm._generate(
            prompts=[llm_input], stop=stop, run_manager=run_manager, **kwargs
        )
        return self._to_chat_result(llm_result)

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        *,
        stream_usage: Optional[bool] = True,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        # changed_line
        final_response = kwargs.pop("final_response_dict", {}).copy()
        if _is_huggingface_endpoint(self.llm):
            kwargs["stream"] = True

            stream_usage = self._should_stream_usage(stream_usage, **kwargs)
            if stream_usage:
                kwargs["stream_options"] = {"include_usage": stream_usage}

            message_dicts, params = self._create_message_dicts(messages, stop)
            params = {**params, **kwargs, "stream": True}

            default_chunk_class: type[BaseMessageChunk] = AIMessageChunk
            for chunk in self.llm.client.chat_completion(
                messages=message_dicts, **params
            ):
                usage = chunk.get("usage")
                if usage:
                    usage_msg = AIMessageChunk(
                        content="",
                        additional_kwargs={},
                        response_metadata={},
                        usage_metadata={
                            "input_tokens": usage.get("prompt_tokens", 0),
                            "output_tokens": usage.get("completion_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0),
                            "input_token_details": {"audio": 0, "cache_read": 0},
                            "output_token_details": {"audio": 0, "reasoning": 0},
                        },
                    )
                    yield ChatGenerationChunk(message=usage_msg)
                    continue

                if len(chunk["choices"]) == 0:
                    continue

                choice = chunk["choices"][0]
                message_chunk = _convert_chunk_to_message_chunk(
                    chunk, default_chunk_class
                )
                generation_info: dict[str, Any] = {}
                if finish_reason := choice.get("finish_reason"):
                    generation_info["finish_reason"] = finish_reason
                    generation_info["model_name"] = self.model_id
                logprobs = choice.get("logprobs")
                if logprobs:
                    generation_info["logprobs"] = logprobs
                default_chunk_class = message_chunk.__class__
                generation_chunk = ChatGenerationChunk(
                    message=message_chunk,
                    generation_info=generation_info or None,
                )

                if run_manager:
                    run_manager.on_llm_new_token(
                        generation_chunk.text,
                        chunk=generation_chunk,
                        logprobs=logprobs,
                    )
                # changed line
                if final_response.get("final_response", None):
                    generation_chunk.message.additional_kwargs.update(final_response)
                yield generation_chunk
        else:
            llm_input = self._to_chat_prompt(messages)
            stream_iter = self.llm._stream(
                llm_input, stop=stop, run_manager=run_manager, **kwargs
            )
            for chunk in stream_iter:
                additional_kwargs = {}
                # changed line
                if final_response.get("final_response", None):
                    additional_kwargs.update(final_response)
                chat_chunk = ChatGenerationChunk(
                    message=AIMessageChunk(content=chunk.text),
                    generation_info=chunk.generation_info,
                    additional_kwargs=additional_kwargs,
                )
                yield chat_chunk

    def with_structured_output(
        self,
        schema: Optional[Union[dict, type[BaseModel]]] = None,
        *,
        method: Literal[
            "function_calling", "json_mode", "json_schema"
        ] = "function_calling",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, Union[dict, BaseModel]]:
        """Model wrapper that returns outputs formatted to match the given schema.

        Args:
            schema:
                The output schema. Can be passed in as:
                    - an OpenAI function/tool schema,
                    - a JSON Schema,
                    - a typedDict class (support added in 0.1.7),

                Pydantic class is currently supported.

            method: The method for steering model generation, one of:

                - "function_calling": uses tool-calling features.
                - "json_schema": uses dedicated structured output features.
                - "json_mode": uses JSON mode.

            include_raw:
                If False then only the parsed structured output is returned. If
                an error occurs during model output parsing it will be raised. If True
                then both the raw model response (a BaseMessage) and the parsed model
                response will be returned. If an error occurs during output parsing it
                will be caught and returned as well. The final output is always a dict
                with keys "raw", "parsed", and "parsing_error".

            kwargs:
                Additional parameters to pass to the underlying LLM's
                :meth:`langchain_core.language_models.chat.BaseChatModel.bind`
                method, such as `response_format` or `ls_structured_output_format`.

        Returns:
            A Runnable that takes same inputs as a :class:`langchain_core.language_models.chat.BaseChatModel`.

            If ``include_raw`` is False and ``schema`` is a Pydantic class, Runnable outputs
            an instance of ``schema`` (i.e., a Pydantic object).

            Otherwise, if ``include_raw`` is False then Runnable outputs a dict.

            If ``include_raw`` is True, then Runnable outputs a dict with keys:
                - ``"raw"``: BaseMessage
                - ``"parsed"``: None if there was a parsing error, otherwise the type depends on the ``schema`` as described above.
                - ``"parsing_error"``: Optional[BaseException]

        """  # noqa: E501
        _ = kwargs.pop("strict", None)
        if kwargs:
            msg = f"Received unsupported arguments {kwargs}"
            raise ValueError(msg)
        is_pydantic_schema = isinstance(schema, type) and is_basemodel_subclass(schema)
        if method == "function_calling":
            if schema is None:
                msg = (
                    "schema must be specified when method is 'function_calling'. "
                    "Received None."
                )
                raise ValueError(msg)
            formatted_tool = convert_to_openai_tool(schema)
            tool_name = formatted_tool["function"]["name"]
            llm = self.bind_tools(
                [schema],
                tool_choice=tool_name,
                ls_structured_output_format={
                    "kwargs": {"method": "function_calling"},
                    "schema": formatted_tool,
                },
            )
            if is_pydantic_schema:
                msg = "Pydantic schema is not supported for function calling"
                raise NotImplementedError(msg)
            output_parser: Union[JsonOutputKeyToolsParser, JsonOutputParser] = (
                JsonOutputKeyToolsParser(key_name=tool_name, first_tool_only=True)
            )
        elif method == "json_schema":
            if schema is None:
                msg = (
                    "schema must be specified when method is 'json_schema'. "
                    "Received None."
                )
                raise ValueError(msg)
            formatted_schema = convert_to_json_schema(schema)
            llm = self.bind(
                response_format={"type": "json_object", "schema": formatted_schema},
                ls_structured_output_format={
                    "kwargs": {"method": "json_schema"},
                    "schema": schema,
                },
            )
            # changed line
            if is_pydantic_schema:
                output_parser: Union[PydanticToolsParser, PydanticOutputParser] = (
                    PydanticOutputParser(pydantic_object=schema)
                )
            else:
                output_parser: Union[  # type: ignore[no-redef]
                    JsonOutputKeyToolsParser, JsonOutputParser
                ] = JsonOutputParser()  # type: ignore[arg-type]

        elif method == "json_mode":
            llm = self.bind(
                response_format={"type": "json_object"},
                ls_structured_output_format={
                    "kwargs": {"method": "json_mode"},
                    "schema": schema,
                },
            )
            output_parser: Union[  # type: ignore[no-redef]
                JsonOutputKeyToolsParser, JsonOutputParser
            ] = JsonOutputParser()  # type: ignore[arg-type]
        else:
            msg = (
                f"Unrecognized method argument. Expected one of 'function_calling' or "
                f"'json_mode'. Received: '{method}'"
            )
            raise ValueError(msg)

        if include_raw:
            parser_assign = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | output_parser, parsing_error=lambda _: None
            )
            parser_none = RunnablePassthrough.assign(parsed=lambda _: None)
            parser_with_fallback = parser_assign.with_fallbacks(
                [parser_none], exception_key="parsing_error"
            )
            return RunnableMap(raw=llm) | parser_with_fallback
        return llm | output_parser

    def _build_tool_call_tasks(self, messages, calls, tool_names, schemas, has_image):
        """Prepares a list of (i, call_name, structured, messages) for batch processing."""
        tasks = []
        for i, call_name in enumerate(calls):
            if call_name not in tool_names:
                continue

            spec = schemas[call_name]

            structured = self.with_structured_output(
                schema=spec, include_raw=True, method="json_schema"
            )

            prefix = "사진과 사용자 응답을 보고" if has_image else "사용자 응답에 대해"
            props = ", ".join(spec["properties"].keys())
            postfix_tool_call_msg = f"\n{prefix} 알맞는 argument인 '{props}'만 key로 포함하는 JSON을 생성합니다."

            msgs = copy.deepcopy(messages)
            if isinstance(msgs[-1].content, str):
                msgs[-1].content += postfix_tool_call_msg
            else:
                msgs[-1].content.append({"type": "text", "text": postfix_tool_call_msg})
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
        max_workers=8,
        tool_prompt_path: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ) -> Runnable[list[BaseMessage], AIMessage]:
        """
        A binder that enables tool-calling for models without native support,
        by using with_structured_output to parse tool selection into
        OpenAI-style AIMessage(tool_calls=...).

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
        formatted = [convert_to_openai_tool(t, strict=strict) for t in tools]
        tool_names, tool_name_description = zip(
            *(
                (
                    t["function"]["name"],
                    f"- {t['function']['name']}: {t['function']['description']}",
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
            has_image = False
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
                for m in messages:
                    if isinstance(m, HumanMessage) and isinstance(m.content, str):
                        m.content = [{"type": "text", "text": m.content}]
                msgs.extend(messages)
                if has_image_url(messages):
                    image_prefix = {"type": "text", "text": self.image_tool_call_msg}
                    if isinstance(msgs[-1], HumanMessage):
                        msgs[-1].content.append(image_prefix)
            else:
                raise TypeError(
                    f"messages must be str or list[BaseMessage], got {type(messages)}"
                )

            # first step: extract tool_name or general response
            response = self.invoke(msgs, **kwargs)

            token_usage_total = response.usage_metadata
            parsed = detect_tool_call(response.content)

            calls = parsed.get("calls", []) if isinstance(parsed, dict) else []
            if not calls and any(isinstance(m, ToolMessage) for m in messages):
                # not choose tool and return general response
                messages.insert(0, SystemMessage(content=self.react_qa_msg))
                for m in messages:
                    if isinstance(m, ToolMessage) and isinstance(m.content, str):
                        if not m.content.startswith(self.mimic_tool_msg):
                            m.content = self.mimic_tool_msg + m.content
                return self.invoke(messages, **kwargs_final)

            # second step: extract tool arguments. supports multiple tool calls.
            lc_tool_calls, oai_tool_calls = [], []

            tasks = self._build_tool_call_tasks(
                messages, calls, tool_names, schemas, has_image
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
                # return results in the same format as OpenAI tool-calling response
                return AIMessage(
                    content="",
                    tool_calls=lc_tool_calls,
                    response_metadata={"token_usage": token_usage_total},
                    additional_kwargs={
                        "tool_calls": oai_tool_calls,
                        "refusal": None,
                    },
                )
            return self.invoke(messages, **kwargs_final)

        return RunnableLambda(_invoke)
