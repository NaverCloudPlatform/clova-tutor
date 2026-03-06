# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any, Iterator, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import AIMessageChunk, BaseMessage, BaseMessageChunk
from langchain_core.outputs import ChatGenerationChunk
from langchain_huggingface import ChatHuggingFace
from langchain_huggingface.chat_models.huggingface import (
    _convert_chunk_to_message_chunk,
    _is_huggingface_endpoint,
)


class ChatHuggingFaceWithUsage(ChatHuggingFace):

    stream_usage: bool = False
    """Whether to include usage metadata in streaming output. If True, an additional
    message chunk will be generated during the stream including usage metadata."""

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

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        *,
        stream_usage: Optional[bool] = True,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:

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
                yield generation_chunk
        else:
            llm_input = self._to_chat_prompt(messages)
            stream_iter = self.llm._stream(
                llm_input, stop=stop, run_manager=run_manager, **kwargs
            )
            for chunk in stream_iter:
                chat_chunk = ChatGenerationChunk(
                    message=AIMessageChunk(content=chunk.text),
                    generation_info=chunk.generation_info,
                )
                yield chat_chunk
