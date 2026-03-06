# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import functools
import re
import sys
import traceback
from functools import wraps
from typing import Any, Callable, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langgraph.types import Command
from typing_extensions import Literal

from assistant.src.hcx_structured_output import PromptToolMessageBundle
from assistant.src.mapping import ErrorType
from assistant.src.schema import (
    Answer,
    Error,
    Explanation,
    ProblemInfo,
    RecommendedProblems,
    ReferenceProblemInfo,
    SubjectInfo,
)
from assistant.src.utils.load_utils import load_default_prompt

MAX_TURN_HISTORY = 3
MAX_TRIES = 3


def get_runnable(obj):
    return RunnableLambda(obj) if obj else RunnablePassthrough()


class LLMRetryableError(Exception):
    def __init__(self, message, attempt_count=None):
        super().__init__(message)
        self.attempt_count = attempt_count


class LLMNonRetryableError(Exception):
    def __init__(
        self,
        node_name: str = "",
        filename: str = "",
        line: int = 0,
        original_exception: Exception = Exception("Unknown error"),
        error_type: Optional[ErrorType] = None,  # ratelimit, parse, unknown.
    ):
        self.node_name = node_name
        self.filename = filename
        self.line = line
        self.original_exception = original_exception
        self.error_type = error_type

        message = f"{node_name}, {filename}:{line} {original_exception}"
        super().__init__(message)


class ParseError(ValueError):
    """Custom exception for parsing errors that includes original text"""

    def __init__(self, message: str, original_text: str = None, **kwargs):
        self.original_text = original_text
        self.additional_data = kwargs
        super().__init__(message)


def retry_on_parse_error(
    node_fn: Callable[[Any], Any] = None,
    max_tries: int = MAX_TRIES,
    fallback_node: str = "default_chat",
    retry_exceptions: tuple = (ValueError,),
) -> Callable[[Any], Any]:
    """
    An wrapper to retry a LangGraph node function on parsing errors (ValueError).
    """

    def decorator_retry(node_fn):
        node_name = node_fn.__name__

        @functools.wraps(node_fn)
        def wrapped(*args, **kwargs):
            # Use structured_logger instead of write_log
            logging_fn = getattr(args[0], "structured_logger", None)
            for attempt in range(1, max_tries + 1):
                try:
                    return node_fn(*args, **kwargs)
                except retry_exceptions as e:
                    error_msg = f"[Retry {attempt+1}/{MAX_TRIES}] ValueError in {node_name}: {e}"

                    # Prepare additional data for logging
                    additional_data = {
                        "attempt": attempt + 1,
                        "max_tries": MAX_TRIES,
                    }

                    # Try to extract user input from state (args[1] is typically the state)
                    user_input = None
                    if (
                        len(args) > 1
                        and hasattr(args[1], "messages")
                        and args[1].messages
                    ):
                        try:
                            user_input = get_text_message(args[1].messages[-1])
                        except Exception:
                            pass

                    # If it's a ParseError with original text, include it
                    if isinstance(e, ParseError) and e.original_text:
                        # Use user input as original_text if available, otherwise use LLM response
                        additional_data["original_text"] = (
                            user_input if user_input else e.original_text
                        )
                        additional_data["llm_response"] = (
                            e.original_text
                        )  # Keep LLM response for debugging
                        additional_data.update(e.additional_data)
                    # Also try to extract original_text from ValueError message if it contains ParseError info
                    elif isinstance(e, ValueError) and "ParseError" in str(e):
                        additional_data["original_text"] = (
                            user_input if user_input else "User input not available"
                        )
                        # Try to extract original_text from the error message or additional_data
                        if hasattr(e, "original_text"):
                            additional_data["llm_response"] = e.original_text
                        if hasattr(e, "additional_data"):
                            additional_data.update(e.additional_data)
                    else:
                        # For other ValueError cases, still try to include user input
                        if user_input:
                            additional_data["original_text"] = user_input

                    if logging_fn:
                        # Use structured_logger.log_error instead of write_log
                        logging_fn.log_error(
                            error_type="parsing_error",
                            error_msg=error_msg,
                            node_name=node_name,
                            additional_data=additional_data,
                        )
                    if attempt >= max_tries - 1:
                        error = Error(
                            type=ErrorType.PARSE,
                            error_msg=error_msg,
                            node_name=node_name,
                        )
                        return Command(update={"error": error}, goto=fallback_node)
                except Exception as e:
                    tb = sys.exc_info()[2]
                    traceback_info = traceback.extract_tb(tb)[-1]
                    filename, line, _, _ = traceback_info
                    filename = filename.split("/")[-1]
                    if logging_fn:
                        logging_fn.log_error(
                            error_type="unknown_error",
                            error_msg=f"Exception in {node_name}, {filename}:{line} {e}",
                        )
                    raise LLMNonRetryableError(
                        node_name=node_name,
                        filename=filename,
                        line=line,
                        original_exception=e,
                        error_type=(
                            e.error_type
                            if hasattr(e, "error_type")
                            else ErrorType.UNKNOWN
                        ),
                    )

        return wrapped

    if node_fn is None:
        return decorator_retry
    else:
        return decorator_retry(node_fn)


def catch_parse_error(
    fn: Callable[[Any], Any], retry_exceptions: tuple = (ValueError, IndexError)
):
    """
    A wrapper to catch parsing errors (ValueError by default) and return a dedicated error message.
    """
    fn_name = fn.__name__

    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except retry_exceptions as e:
            # Preserve ParseError if it's a ParseError
            if isinstance(e, ParseError):
                raise e
            else:
                raise ValueError(f"Parsing error in {fn_name}: {e}")
        except Exception as e:
            raise e

    return wrapped


# deprecated
def check_parse_error(fn: Callable[[Any], str]) -> Callable[[Any], str]:
    """
    A decorator to check parsing error in state and return "parsing_error" if True.
    """
    fn_name = fn.__name__

    @wraps(fn)
    def wrapped(*args, **kwargs) -> Command[Literal["parsing_error"]]:
        breakpoint()
        if args[0].error is not None and args[0].error.type == ErrorType.PARSE:
            return Command(goto="parsing_error")
        return fn(*args, **kwargs)

    return wrapped


def preprocess_query(query: list | dict, **kwargs):

    def query2content(user_query: List[dict]):
        text = ""
        image_url = []
        if isinstance(user_query.content, list):
            for _q in user_query.content:
                if _q["type"] == "text":
                    text += _q.get("text") or _q.get("content")
                elif _q["type"] == "image" or _q["type"] == "image_url":
                    image_url.append(_q.get("image_url") or _q["content"])
        return text, image_url

    # when additional kwargs are passed
    if isinstance(query, dict) and "messages" in query:
        arguments = query
        query = query["messages"]
    else:
        arguments = {}

    curr_query, url = query2content(query[-1])
    history = messages_to_string(query[:-1])

    if curr_query:
        arguments.pop("user_query", None)

    if not url:
        return {"user_query": curr_query, "history": history, **arguments}
    else:
        return {
            "user_query": curr_query,
            "image_url": url,
            "history": history,
            **arguments,
        }


def convert_message_content(messages: list[BaseMessage]) -> list[BaseMessage]:
    converted = []
    for message in messages:
        if isinstance(message.content, list):
            new_content = []
            for block in message.content:
                if isinstance(block, dict):
                    block_type = block.get("type")

                    if block_type == "text":
                        text_val = block.get("text") or block.get("content") or ""
                        new_content.append({"type": "text", "text": text_val})

                    elif block_type == "image":
                        url = block.get("content") or block.get("url")
                        if url:
                            new_content.append(
                                {"type": "image_url", "image_url": {"url": url}}
                            )

                    else:
                        # 이미 올바른 형식 (image_url 등)은 그대로
                        new_content.append(block)

                else:
                    new_content.append(block)

            converted_msg = message.__class__(
                content=new_content,
                **{k: v for k, v in message.__dict__.items() if k != "content"},
            )
            converted.append(converted_msg)
        else:
            converted.append(message)
    return converted


def concat_messages(messages: list[BaseMessage]) -> PromptToolMessageBundle:
    human_msg = None
    system_msg = None

    has_ai = any(isinstance(m, AIMessage) for m in messages)

    for m in messages:
        if isinstance(m, SystemMessage):
            system_msg = m.content if m.content else None
        elif isinstance(m, HumanMessage) and not has_ai:
            if isinstance(m.content, list):
                text_blocks = [
                    block.get("text") or block.get("content")
                    for block in m.content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if text_blocks:
                    human_msg = text_blocks[-1]
            else:
                human_msg = m.content.strip() or None

    prompt = PromptToolMessageBundle(system=system_msg, user=human_msg)
    return prompt


def get_dialogue(input_dict: dict):
    return (
        input_dict.get("history", "") + "\n사용자: " + input_dict.get("user_query", "")
    )


def get_friendly_dialogue(input_dict: dict):
    dialogue = input_dict.get("history", "")
    if dialogue:
        dialogue = dialogue.replace("AI튜터: ", "클로바: ")
        dialogue = dialogue.replace("사용자: ", "친구: ")
    return dialogue + "\n친구: " + input_dict.get("user_query", "")


def get_subject_info(input_dict: dict):
    subject_info = input_dict.get("subject_info", "")
    if subject_info:
        if subject_info.subject == "영어":
            # english
            if subject_info.section:
                subject_info = f"""subject: {subject_info.subject}\nsection: {subject_info.section}"""
            else:
                subject_info = f"""subject: {subject_info.subject}\nsection: {subject_info.section}\ntopic: {subject_info.topic}"""
        else:
            # math
            subject_info = f"""subject: {subject_info.subject}\nsection: {subject_info.section}\ntopic: {subject_info.topic}"""
    return subject_info


def get_problem_info(input_dict: dict):
    problem_info = input_dict.get("problem_info", None)
    if problem_info == "None" or problem_info is None:
        return None
    else:
        explanation_str = "\n".join(
            f"{k}단계: '{v}'"
            for k, v in problem_info.explanation.model_dump()["text"].items()
        )
        answer_text = problem_info.answer.text if problem_info.answer else ""
        problem_info = f"""과목: {problem_info.subject_info.subject}
문항: {problem_info.question}
풀이: {explanation_str}
정답: {answer_text}"""
        return problem_info


def get_problem_qa(input_dict: dict):
    problem_info = input_dict.get("problem_info", "None")
    if problem_info != "None":
        question = problem_info.question if problem_info else ""
        answer = problem_info.answer if problem_info else ""
        return f"question: {question}\nanswer: {answer}"
    else:
        return "None"


def get_student_profile(input_dict: dict):
    student_profile = input_dict.get("student_profile", "")
    if student_profile:
        grade = get_grade_to_str(student_profile.grade)
        student_profile = f"""semester: {student_profile.semester}
grade: {grade}"""
    return student_profile


def get_grade_to_str(grade: int) -> str:
    if grade < 7:
        grade = f"초등학교 {grade}학년"
    elif grade < 10:
        grade = f"중학교 {grade - 6}학년"
    elif grade < 13:
        grade = f"고등학교 {grade - 9}학년"
    return grade


def get_query_with_context(
    dialogue: list,
    problem_info: Optional[ProblemInfo] = None,
):
    if dialogue:
        dialogue = messages_to_string(dialogue)
        dialogue = get_dialogue({"history": dialogue}).replace("\n사용자:", "").strip()
    else:
        dialogue = ""

    if problem_info:
        problem_info = get_problem_info({"problem_info": problem_info})
    else:
        problem_info = ""

    return f"{problem_info}\n{dialogue}"


def get_reference_document(input_dict: dict):
    reference_document = ""
    for document in input_dict.get("reference_document", []):
        reference_document += f"개념: {document['metadata']['concept']}\n$${document['metadata']['latex']}$$\n설명: {document['metadata']['description']}\n\n"
    return reference_document


def get_format_instructions(input_dict: dict):
    output_schema = input_dict.get("output_schema", "")
    if output_schema:
        lines = []
        for field_name, field in output_schema.model_fields.items():
            desc = field.description or "설명 없음"
            typ = (
                field.annotation.__name__
                if hasattr(field.annotation, "__name__")
                else str(field.annotation)
            )
            lines.append(f"- {field_name} ({typ}): {desc}")
        return (
            "다음 형식으로 JSON 객체를 생성하세요:\n{\n"
            + ",\n".join([f'  "{f}": ...' for f in output_schema.model_fields])
            + "\n}\n\n각 항목의 의미:\n"
            + "\n".join(lines)
        )
    else:
        return ""


def rename_content_to_text(
    message: HumanMessage | AIMessage,
) -> HumanMessage | AIMessage:
    if isinstance(message, HumanMessage):
        content = message.content[0]
        if content.get("type") == "text" and "content" in content:
            new_content = [{"type": content["type"], "text": content["content"]}]
        else:
            new_content = content
        return HumanMessage(
            content=new_content,
            additional_kwargs=message.additional_kwargs,
            response_metadata=message.response_metadata,
        )
    else:
        return message


def preprocessing_msgs_for_tool(messages: HumanMessage | AIMessage):
    return [rename_content_to_text(message) for message in messages]


def extend_prompt_arguments(prompt_str: str, input_args: dict) -> dict:
    common_prompts = load_default_prompt("eduqa_common")
    for prompt_name, prompt in common_prompts.items():
        if prompt_name in prompt_str:
            input_args[prompt_name] = prompt

    if "{dialogue}" in prompt_str:
        input_args["dialogue"] = get_dialogue(input_args)

    if "{friendly_dialogue}" in prompt_str:
        input_args["friendly_dialogue"] = get_friendly_dialogue(input_args)

    if "{subject_info}" in prompt_str:
        input_args["subject_info"] = get_subject_info(input_args)

    if "{student_profile}" in prompt_str:
        input_args["student_profile"] = get_student_profile(input_args)

    if "{problem_info}" in prompt_str:
        input_args["problem_info"] = get_problem_info(input_args)

    if "{problem_qa}" in prompt_str:
        input_args["problem_qa"] = get_problem_qa(input_args)

    if "{reference_document}" in prompt_str:
        input_args["reference_document"] = get_reference_document(input_args)

    if "{unknown_concept}" in prompt_str:
        input_args["unknown_concept"] = get_unknown_concept(
            input_args["unknown_concept"]
        )

    if "{format_instructions}" in prompt_str:
        input_args["format_instructions"] = get_format_instructions(input_args)

    if "level_instruction" in input_args:
        input_args["level_instruction"] = common_prompts[
            "grade_instruction_math"
        ].format(grade=get_grade_to_str(input_args["level_instruction"]))

    return input_args


def generate_multiturn_history(input_dict: dict) -> list:
    """Generate a multi-turn history"""
    msg = input_dict.get("messages", [])
    if not msg:
        return []

    msg = msg[-MAX_TURN_HISTORY * 2 :]
    dialogue_history = []

    for _msg in msg:
        content = []
        if isinstance(_msg.content, str):
            content.append({"type": "text", "text": _msg.content})
        else:
            for _content in _msg.content:
                if _content["type"] == "text":
                    if _content.get("content"):
                        content.append({"type": "text", "text": _content["content"]})
                    elif _content.get("text"):
                        content.append(_content)
                elif _content["type"] == "image_url":
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": _content["image_url"]["url"]},
                        }
                    )

        dialogue_history.append(
            _msg.__class__(
                content=content,
                additional_kwargs=_msg.additional_kwargs,
            )
        )
    return dialogue_history


def build_user_message(prompt_template: str, arguments: dict) -> list:

    # get history as multi-turn dialogue
    if prompt_template in {"{dialogue}\n", "{friendly_dialogue}\n"}:
        user_msg = generate_multiturn_history(arguments)

    # otherwise, format the prompt template
    else:
        user_msg = prompt_template.format(**arguments)
        user_msg = [HumanMessage(content=[{"type": "text", "text": user_msg}])]
    return user_msg


def preprocess_prompt(
    prompt_name: str = "eduqa",
    chain_name: str = "default_chat",
    arguments: dict = {},
    use_tool_call_msg: Optional[str] = None,
):
    prompt = load_default_prompt(prompt_name).get(chain_name, {})
    system_prompt_template = prompt.get("system_prompt", "")
    user_prompt_template = prompt.get("user_prompt", "")

    inputs = extend_prompt_arguments(
        system_prompt_template + user_prompt_template, arguments
    )

    system_prompt = system_prompt_template.format(**inputs)
    if "level_instruction" in inputs:
        system_prompt += "\n" + inputs["level_instruction"]
    human_msg = build_user_message(user_prompt_template, inputs)
    if use_tool_call_msg:
        human_msg += [
            HumanMessage(
                content=[{"type": "text", "text": use_tool_call_msg}],
            )
        ]

    # add image_url to human message if exists
    if "image_url" in inputs:
        if not isinstance(inputs["image_url"], list):
            inputs["image_url"] = [inputs["image_url"]]

        human_msg[-1].content.append(
            {"type": "image_url", "image_url": {"url": inputs["image_url"][0]}}
        )
        human_msg[-1].additional_kwargs["has_image"] = True

        add_human_msgs = []
        # case of multiple images
        if len(inputs["image_url"]) > 1:
            for img in inputs["image_url"][1:]:
                add_human_msgs.append(
                    HumanMessage(
                        content=[{"type": "image_url", "image_url": {"url": img}}],
                        additional_kwargs={"has_image": True},
                    )
                )

        human_msg = add_human_msgs + human_msg
    if system_prompt:
        system_msg = SystemMessage(content=system_prompt)
        return [system_msg, *human_msg]
    else:
        return human_msg


def get_message(
    state,
    message_type: AIMessage | HumanMessage | SystemMessage | list,
    idx: int = -1,
):
    messages = state.messages

    # return None if messages is empty
    if not messages:
        return None

    if not isinstance(message_type, list):
        message_type = [message_type]

    target_messages = []
    for msg in messages:
        if type(msg) in message_type:
            target_messages.append(msg)

    # return None if target_messages is empty
    if not target_messages:
        return None

    try:
        return target_messages[idx]
    except IndexError:
        return None


def messages_to_string(messages: list):
    result = []
    for msg in messages:
        if isinstance(msg.content, dict):
            content = msg.content["content"]
        elif isinstance(msg.content, list):
            content = ""
            for _msg_content in msg.content:
                if _msg_content["type"] == "text":
                    content = _msg_content.get("content", _msg_content.get("text"))
                    break
        else:
            content = msg.content
        content = content.replace("\n", " ")

        if isinstance(msg, HumanMessage):
            if content.startswith("과거 질문 내역:"):
                result.append(content)
            else:
                result.append(f"사용자: {content}")
        elif isinstance(msg, AIMessage):
            result.append(f"AI튜터: {content}")
    return "\n".join(result[-MAX_TURN_HISTORY * 2 :])


def get_text_message(message: AIMessage | HumanMessage | SystemMessage):
    text_message = []
    for msg in message.content:
        if msg["type"] == "text":
            text_message.append(msg["content"])
    return "\n".join(text_message)


def get_image_message(message: AIMessage | HumanMessage | SystemMessage):
    # assuming message.content includes a single image
    for msg in message.content:
        if msg["type"] == "image":
            return msg["content"]
    return ""  # return empty string if no image found


def convert_to_problem_info(subject: str, doc_info: dict) -> ProblemInfo:
    data_source = "ebs"

    if re.match(r"^\[.*\]$", doc_info.get("section").strip()):
        section = re.findall(r"'(.*?)'", doc_info.get("section"))
    else:
        section = doc_info.get("section")

    subject_info = SubjectInfo(
        subject=subject,
        section=section,
        unit=doc_info.get("unit", ""),
        topic=[doc_info.get("topic")] if doc_info.get("topic") else [],
    )

    parts = [
        part.strip()
        for part in doc_info.get("explanation", "").split(".")
        if part.strip()
    ]  # split the explanation

    image_url = doc_info.get("image_path", "")

    problem_info = ProblemInfo(
        problem_id=doc_info.get("problem_id", ""),
        question=doc_info.get("problem", ""),
        explanation=Explanation(text={i + 1: part for i, part in enumerate(parts)}),
        answer=Answer(text=doc_info.get("correct_answers", "")),
        level=int(doc_info.get("level", 0)),
        subject_info=subject_info,
        data_source=data_source,
        has_image=True if image_url else False,
        image_url=image_url,
    )

    return problem_info


def convert_to_reference_problems(
    subject: str,
    documents: List[tuple],
) -> List[ReferenceProblemInfo]:

    result = []
    for doc, score in documents:
        metadata = doc["metadata"]
        problem_info = convert_to_problem_info(subject, metadata)

        recommended = ReferenceProblemInfo(
            problem_info=problem_info,
            similarity_score=score,
        )
        result.append(recommended)
    return result


def get_problem_group_by_level(
    recommended_list: List[ReferenceProblemInfo],
) -> RecommendedProblems:
    easy, normal, hard = [], [], []
    # Level standard based on EBS: 1=easy, 2=normal, 3=hard
    for item in recommended_list:
        level = item.problem_info.level
        if level == 3:
            hard.append(item)
        elif level == 2:
            normal.append(item)
        elif level == 1:
            easy.append(item)
        else:
            normal.append(item)

    return RecommendedProblems(easy=easy, normal=normal, hard=hard)


def get_equal_problem(
    recommended_problems: RecommendedProblems, threshold: int = 0.98
) -> Optional[ProblemInfo]:
    all_problems = (
        recommended_problems.easy
        + recommended_problems.normal
        + recommended_problems.hard
    )

    # filter problems exceeding the threshold
    candidates = [p for p in all_problems if p.similarity_score >= threshold]
    if not candidates:
        return None  # No cadidates

    best = max(candidates, key=lambda p: p.similarity_score)
    return best.problem_info


def remove_equal_problem(
    recommended_problems: RecommendedProblems, equal_problem: ProblemInfo
):
    for difficulty in ["easy", "normal", "hard"]:
        problems = getattr(recommended_problems, difficulty)
        filtered = [prob for prob in problems if prob.problem_info != equal_problem]
        setattr(recommended_problems, difficulty, filtered)


def get_voca_additional_table(response_style_voca_additional):
    mapping = {1: "유의어", 2: "반의어", 3: "어원", 4: "변화형", 5: "관용구"}
    if not isinstance(response_style_voca_additional, dict):
        return ""
    parts = []
    for word, codes in response_style_voca_additional.items():
        labels = [mapping[code] for code in codes if code in mapping]
        if labels:
            joined = ", ".join(labels)
            parts.append(f"{word}의 {joined}")
    return "및 ".join(parts)


def get_unknown_concept(unknown_list):
    if unknown_list:
        return f"unknown_concept: {unknown_list[0]['unknown_concept']}\nunknown_concept_reason: {unknown_list[0]['unknown_concept_reason']}"
    else:
        # key_concept에 저장된 값이 없는 경우
        return "unknown_concept: \nunknown_concept_reason: "


def safe_tool_name(t):
    return getattr(t, "name", getattr(t, "__name__", type(t).__name__))


def attach_summed_usage(messages: list) -> list:
    ai_messages = [m for m in messages if isinstance(m, AIMessage)]
    total_input = 0
    total_output = 0
    total_tokens = 0

    for msg in ai_messages:
        usage = msg.usage_metadata or msg.response_metadata.get("token_usage", None)
        if usage:
            total_input += usage.get("input_tokens", 0)
            total_output += usage.get("output_tokens", 0)
            total_tokens += usage.get("total_tokens", 0)

    if ai_messages:
        last_ai = ai_messages[-1]
        model_response_token_usage = last_ai.usage_metadata
        last_ai.usage_metadata = {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_tokens,
            "model_response_token_usage": model_response_token_usage,
        }
    return messages
