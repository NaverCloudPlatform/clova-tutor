# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import time

from langchain_naver import ChatClovaX
from langchain_openai import ChatOpenAI

from assistant.src.hcx_structured_output import ChatClovaXHSO
from assistant.src.mapping import ErrorType
from assistant.src.post_process import (
    common_post_process,
    eng_post_process,
    math_post_process,
)
from assistant.src.schema import ModelParam
from assistant.src.utils.call_utils import (
    LLMNonRetryableError,
    preprocess_prompt,
    preprocess_query,
)
from assistant.src.utils.load_utils import load_yaml
from assistant.src.utils.structured_logger import StructuredLogger

MAX_TRIES = 3


class CallManager:
    """CallManager is a base class for building and managing LLM (Language Model) calls."""

    """
    ModelChainBuilder is a class that sets up and executes LLM (Language Model)-based chains.

    Attributes:
        model_param (ModelParam): Default parameters for the model.
        logger (Logger): Logger object for managing logs.

    Methods:
        invoke(query): Invokes the model's response to a given query.
    """

    def __init__(self, logger, default_system_str, **kwargs):
        # self.logger = logger  # No longer needed
        thread_id = kwargs.get("thread_id", "unknown")
        self.structured_logger = StructuredLogger(
            logger, thread_id
        )  # New logging system (Use new logging system)

        self.api_info = load_yaml("assistant/api_info.yaml")

        # initialize llm based on model_param
        self.model_param = kwargs.get("model_param", ModelParam())
        self.llm = self.set_llm(self.model_param)

        # initialize tool llm
        # TODO: model_parma 적용
        self.tool_llm = ChatClovaXHSO(
            model="hcx-005", default_system_str=default_system_str
        )

        # initialize post-processing functions
        self.post_process_map = {
            "eng": eng_post_process,
            "math": math_post_process,
            "common": common_post_process,
        }

    def __set_hcx(
        self,
        model_name: str = None,
        model_param: ModelParam = None,
        disable_streaming: str = "tool_calling",
    ):
        if model_name is None:
            model_name = self.model_param.model

        param = model_param if model_param else ModelParam(model=model_name)
        chatclovax_config = {
            **self.api_info[model_name],
            **param.model_dump(exclude="model", exclude_none=True),
        }
        llm = ChatClovaX(**chatclovax_config, disable_streaming=disable_streaming)
        return llm

    def __set_gpt(self, model_name: str = "gpt", model_param: ModelParam = None):
        param = model_param if model_param else ModelParam(model=model_name)
        gpt_config = {**self.api_info["gpt"]}
        llm = ChatOpenAI(
            **gpt_config,
            **param.model_dump(
                include={"model", "max_tokens", "temperature"}, exclude_none=True
            ),
        )
        return llm

    def set_llm(self, model_param: ModelParam):
        model_name = model_param.model
        # setting model
        if "hcx" in model_name:
            llm = self.__set_hcx(model_name, model_param)
        elif "gpt" in model_name:
            llm = self.__set_gpt(model_name, model_param)
        else:
            raise ValueError(f"Unsupported model name: {model_name}")
        return llm

    def set_tool_llm(self, model_param: ModelParam):
        """
        tool_llm에 model_param/추가 파라미터를 반영해서 인스턴스를 만든다.
        지금은 HCX HSO 한 모델만 쓰지만, 필요하면 확장 가능.
        """
        # TODO: 필요 시 api_info/param 반영
        return self.tool_llm

    def generate_prompt(self, prompt_name: str, arguments: dict = {}):
        """
        Generate a prompt based on the given prompt name and arguments.

        Args:
            prompt_name (str): The name of the prompt to be generated.
            arguments (dict, optional): Additional arguments for the prompt.

        Returns:
            str: The generated prompt.
        """
        if "/" not in prompt_name:
            raise ValueError(
                "Prompt name must be in the format of '{prompt_file_name}/{template_name}'"
            )

        prompt_name, template_name = prompt_name.split("/", 1)
        arguments = preprocess_query(arguments)
        return preprocess_prompt(prompt_name, template_name, arguments)

    def invoke(
        self,
        prompt_name: str,
        arguments: dict = {},
        model_param: ModelParam = None,
        additional_params: dict = {},
    ):
        """
        Invoke the model's response to a given query.

        Args:
            prompt_name (str): The name of the prompt to be used. It is expected to in a format of '{prompt_file_name}/{template_name}', e.g., 'eduqa/default_chat'.
            arguments (dict, optional): Additional arguments for the prompt.
            model_param (ModelParam, optional): Model parameters to override the default.
            additional_params (dict, optional): Additional parameters to be merged with model_param.

        Returns:
            str: The response generated by the model.
        """
        start_time = time.time()

        # use default llm if model_param and additional_params are None
        if model_param is None and additional_params is None:
            llm = self.llm
        else:
            # set llm with model_param and additional_params
            model_param = self.model_param if model_param is None else model_param
            for key, value in additional_params.items():
                if hasattr(model_param, key):
                    setattr(model_param, key, value)

            # update_subject_info 경우 HyperClovaX 스트리밍 비활성화
            if "update_subject_info" in prompt_name:
                llm = self.__set_hcx(
                    model_param.model, model_param, disable_streaming=True
                )
            else:
                llm = self.set_llm(model_param)

        # get llm inputs
        arguments = preprocess_query(arguments)
        inputs = self.generate_prompt(prompt_name, arguments)
        template_name = prompt_name.split("/")[-1]

        for attempt in range(1, MAX_TRIES + 1):
            try:
                response = llm.invoke(inputs)
                break  # exit loop if no exception occurs
            except Exception as error:
                # raise error if max retry is reached
                if attempt == MAX_TRIES:
                    raise LLMNonRetryableError(
                        original_exception=error, error_type=ErrorType.RATELIMIT
                    )

                error_code = getattr(error, "code", None)
                if error_code and str(error_code).startswith(
                    "429"
                ):  # retry after wait_time if Too many requests error occurs
                    wait_time = 2**attempt
                    self.structured_logger.log_warning(
                        f"Rate limit error - retry {attempt+1}/{MAX_TRIES}",
                        {
                            "error": str(error),
                            "wait_time_seconds": wait_time,
                            "attempt": attempt + 1,
                            "max_tries": MAX_TRIES,
                            "template_name": template_name,
                        },
                    )
                    time.sleep(wait_time)
                    continue

        # post-processing response if post_processing is provided
        post_process = self.post_process_map["common"]
        for key, module in self.post_process_map.items():
            if key in prompt_name:
                post_process = module
                break
        post_process = getattr(post_process, f"postprocess_{template_name}", None)

        result = post_process(response) if post_process else response

        elapsed_time = time.time() - start_time

        self.structured_logger.log_llm_call(
            template_name=template_name,
            execution_time_ms=elapsed_time * 1000,  # Convert to milliseconds
            usage=response.usage_metadata or {},
            model=self.model_param.model,
            additional_data={"post_processed": post_process is not None},
        )

        return result

    def invoke_tool(
        self,
        prompt_name: str,
        arguments: dict | None = None,
        tools: list | None = None,
        model_param: ModelParam | None = None,
        max_retries_tool: int = 5,
    ):
        # build prompt → bind tools → invoke llm → parse tool_calls
        if arguments is None:
            arguments = {}
        if tools is None:
            tools = []
        if not tools:
            raise ValueError("invoke_tool requires at least 1 tool.")

        start_time = time.time()
        template_name = prompt_name.split("/")[-1]

        llm = self.set_tool_llm(model_param)

        messages = self.generate_prompt(prompt_name, arguments)
        tool_bind_llm = llm.bind_tools(tools, max_retries=max_retries_tool)

        # invoke llm
        for attempt in range(1, MAX_TRIES + 1):
            try:
                response = tool_bind_llm.invoke(messages)
                break
            except Exception as error:
                if attempt == MAX_TRIES:
                    raise LLMNonRetryableError(
                        original_exception=error, error_type=ErrorType.RATELIMIT
                    )
                error_code = getattr(error, "code", None)
                if error_code and str(error_code).startswith("429"):
                    wait_time = 2**attempt
                    self.structured_logger.log_warning(
                        f"[tool] Rate limit - retry {attempt+1}/{MAX_TRIES}",
                        {
                            "error": str(error),
                            "wait_time_seconds": wait_time,
                            "attempt": attempt + 1,
                            "max_tries": MAX_TRIES,
                            "template_name": template_name,
                        },
                    )
                    time.sleep(wait_time)
                    continue

        tool_calls = getattr(response, "tool_calls", []) or []

        elapsed = time.time() - start_time
        self.structured_logger.log_llm_call(
            template_name=template_name,
            execution_time_ms=elapsed * 1000,
            usage=getattr(response, "usage_metadata", {}) or {},
            model=self.model_param.model,
            additional_data={
                "is_tool_call": True,
                "tool_calls_count": len(tool_calls),
                "tools": [t.get("name") for t in tool_calls if isinstance(t, dict)],
            },
        )
        return response

    # deprecated: for future use
    def make_tool_chain(
        self,
        prompt_name: str,
        arguments: dict | None = None,
        tools: list | None = None,
        model_param: ModelParam | None = None,
        max_retries_tool: int = 5,
    ):
        # build prompt → bind tools → invoke llm → parse tool_calls
        if arguments is None:
            arguments = {}
        if tools is None:
            tools = []
        if not tools:
            raise ValueError("invoke_tool requires at least 1 tool.")

        start_time = time.time()
        template_name = prompt_name.split("/")[-1]

        llm = self.set_tool_llm(model_param)

        messages = self.generate_prompt(prompt_name, arguments)
        tool_bind_llm = llm.bind_tools(tools, max_retries=max_retries_tool)

        # invoke llm
        for attempt in range(1, MAX_TRIES + 1):
            try:
                response = tool_bind_llm.invoke(messages)
                break
            except Exception as error:
                if attempt == MAX_TRIES:
                    raise LLMNonRetryableError(
                        original_exception=error, error_type=ErrorType.RATELIMIT
                    )
                error_code = getattr(error, "code", None)
                if error_code and str(error_code).startswith("429"):
                    wait_time = 2**attempt
                    self.structured_logger.log_warning(
                        f"[tool] Rate limit - retry {attempt+1}/{MAX_TRIES}",
                        {
                            "error": str(error),
                            "wait_time_seconds": wait_time,
                            "attempt": attempt + 1,
                            "max_tries": MAX_TRIES,
                            "template_name": template_name,
                        },
                    )
                    time.sleep(wait_time)
                    continue

        tool_calls = getattr(response, "tool_calls", []) or []

        elapsed = time.time() - start_time
        self.structured_logger.log_llm_call(
            template_name=template_name,
            execution_time_ms=elapsed * 1000,
            usage=getattr(response, "usage_metadata", {}) or {},
            model=self.model_param.model,
            additional_data={
                "is_tool_call": True,
                "tool_calls_count": len(tool_calls),
                "tools": [t.get("name") for t in tool_calls if isinstance(t, dict)],
            },
        )
        return response
