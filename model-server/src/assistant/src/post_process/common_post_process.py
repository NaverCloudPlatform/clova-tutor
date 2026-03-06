# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
import re

from langchain.output_parsers import PydanticOutputParser

from assistant.src.utils.call_utils import catch_parse_error
from assistant.src.utils.data_utils import convert_to_json_compatible_str
from assistant.src.utils.load_utils import load_template


def remove_formatting(response: str):
    return re.sub(r"^<?\s?답변\s?>?\s?:\s?", "", response.strip())


def remove_bullet_points(response: str):
    bullet_points = ["-", "*", "•"]
    for bullet in bullet_points:
        escaped_bullet = re.escape(bullet)
        response = re.sub(rf"\s?{escaped_bullet}\s?", "", response)
    return response


def remove_template(response: str):
    response = response.replace("<답변>", "")
    return response.strip("\n").strip()


def parse_key_values(response: str) -> dict:
    result = {}
    for line in response.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        parts = line.split(":", 1)
        key, value = parts
        key = remove_bullet_points(key)
        result[key.strip()] = value.strip()
    return result


@catch_parse_error
def parse_response(schema_object, default_value: dict = None):
    parser = PydanticOutputParser(pydantic_object=schema_object)

    def parse(response_payload):
        response, usage_metadata = (
            response_payload.content,
            response_payload.usage_metadata,
        )

        try:
            response = (
                response.replace("None", "null")
                .replace("False", "false")
                .replace("True", "true")
            )
            parsed_response = parser.parse(response)
        except:
            if (
                default_value is not None
            ):  # if default_value is empty dict, return schema_object with default values defined in the schema
                parsed_response = schema_object(**default_value)
            else:
                parsed_response = None
        return parsed_response, usage_metadata

    return parse


def postprocess_streaming_message(msg, is_first, wait, response_buffer):
    """
    Determine if the message is a valid response (i.e., not a prefix for formatting)
    and update the response buffer.

    Args:
        msg: langchain_core.messages.ai.AIMessageChunk
        is_first: bool, whether the message is the first token
        wait: bool, whether to wait for the next token
        response_buffer: str, the response buffer
    Returns:
        msg: langchain_core.messages.ai.AIMessageChunk
        is_first: bool
        wait: bool
        response_buffer: str
        skip: bool, whether to skip the message
    """

    def is_valid_response(curr_normalized_response_buffer, skip_word):
        nonlocal wait, is_first, skip
        if len(curr_normalized_response_buffer) >= len(skip_word):
            if curr_normalized_response_buffer == skip_word:
                wait = False
                is_first = True
                skip = True
            else:
                # yield the response
                wait = False
                skip = False
                msg.content = response_buffer
        else:
            # wait for the next token
            skip = True

    # process react response
    if msg and isinstance(msg.content[0], dict):
        content = msg.content[0]["text"].strip()
    else:
        content = msg.content.strip()

    # check the first token
    content = msg.content.strip()

    if is_first:
        if content:
            is_first = False
            if content in {"답변", "답", "사용", "클로", "AI"}:
                response_buffer += msg.content
                wait = True
                skip = True
                return (
                    msg,
                    is_first,
                    wait,
                    response_buffer,
                    skip,
                )
            else:
                # remove redundant spaces
                skip = False
                msg.content = content.lstrip()
        else:
            # skip the empty first token
            skip = True
            return msg, is_first, wait, response_buffer, skip

    if wait:
        skip = True
        response_buffer += msg.content
        normalized_response_buffer = response_buffer.replace(" ", "")

        # check "답변:"
        if normalized_response_buffer.startswith("답변"):
            is_valid_response(normalized_response_buffer, "답변:")
            response_buffer = re.sub(r"답변\s?:\s?", "", response_buffer)
            return msg, is_first, wait, response_buffer, skip

        # check "클로바:"
        elif normalized_response_buffer.startswith("클로"):
            is_valid_response(normalized_response_buffer, "클로바:")
            response_buffer = re.sub(r"클로바\s?:\s?", "", response_buffer)
            return msg, is_first, wait, response_buffer, skip

        # check "AI튜터:"
        elif normalized_response_buffer.startswith("AI"):
            is_valid_response(normalized_response_buffer, "AI튜터:")
            response_buffer = re.sub(r"AI\s?튜터\s?:\s?", "", response_buffer)
            return msg, is_first, wait, response_buffer, skip

        # check "사용자요청:"
        elif normalized_response_buffer.startswith("사용"):
            # skip "사용자요청:"
            if len(normalized_response_buffer) >= len("사용자요청:"):
                if normalized_response_buffer == "사용자요청:":
                    # wait until 답변:
                    # wait = True
                    response_buffer = re.sub(
                        r"사용자\s?요청\s?:\s?", "", response_buffer
                    )
                    skip = True
                    return msg, is_first, wait, response_buffer, skip
                else:
                    # yield the response
                    wait = False
                    skip = False
                    msg.content = response_buffer
            else:
                # wait for the next token
                skip = True
                return msg, is_first, wait, response_buffer, skip

        # check the case of "답변:" following "사용자요청:"
        else:
            if msg.content.strip() == "답변" or msg.content.strip() == "답":
                # reset response buffer
                response_buffer = msg.content
                skip = True
            return msg, is_first, wait, response_buffer, skip

    skip = False
    return msg, is_first, wait, response_buffer, skip


def llm_post_processing_filtering_evaluator(output):
    try:
        output = (
            output.content.replace("- json 형식 답변: ", "")
            .replace("json", "")
            .replace("```", "")
            .strip()
        )
        if not output.startswith("{"):
            output = "{" + output + "}"
        output = convert_to_json_compatible_str(output)
        return json.loads(output)
    except json.JSONDecodeError as e_inner:
        print(f"Second JSONDecodeError: {e_inner}")
        raise ValueError(f"Cannot decode JSON: {output}")


def postprocess_update_context(response_payload: str):
    # TODO: error handling
    response = response_payload.content
    response = remove_formatting(response)

    match = re.search(
        r"is_related\s*:\s*(True|False)\s*[\r\n]+persuasion\s*:\s*(.+)",
        response,
        re.DOTALL,
    )
    if not match:
        raise ValueError

    is_related = match.group(1).strip().lstrip(":").strip().lower() == "true"
    response = match.group(2).strip().lstrip(":").strip()

    return {
        "is_related": is_related,
        "response": response,
    }, response_payload.usage_metadata


def postprocess_get_semantics(response_payload: str):
    response = response_payload.content
    response = remove_formatting(response)
    response = response.lower().strip()

    if response.startswith("yes"):
        return True, response_payload.usage_metadata
    elif response.startswith("no"):
        return False, response_payload.usage_metadata


def fix_explanation(json_str: str) -> str:
    json_str = convert_to_json_compatible_str(json_str)

    # extract "explanation" block
    explanation_match = re.search(r'"explanation"\s*:\s*{([^}]*)}', json_str, re.DOTALL)
    if not explanation_match:
        return json_str  # no explanation block found

    raw_block = explanation_match.group(1)

    fixed_lines = []
    for line in raw_block.splitlines():
        if not line.strip():
            continue

        # key without quotes
        if re.search(r'^\s*"?\d+"?\s*:\s*', line):
            line = re.sub(r'^\s*"?(\d+)"?\s*:\s*', r'"\1": ', line)

        # value without quotes
        if re.search(r'"\d+"\s*:\s*', line):
            key, value = line.split(":", 1)
            value = value.strip('" ,')
            value = '"' + value + '",'
            line = f"{key}: {value}"

        # append to fixed lines if line has a valid key-value pair
        if re.search(r'"\d+"\s*:\s*"', line):
            fixed_lines.append(line.strip())
        else:
            line = line.strip('", ')
            if len(fixed_lines) > 0:
                # append to the last line if it is not empty
                fixed_lines[-1] = fixed_lines[-1].rstrip('", ') + "\\\\n" + line + '",'

    # reconstruct explanation as dict
    fixed_dict = "\n    ".join([line.strip() for line in fixed_lines])
    fixed_dict = fixed_dict.rstrip(",")  # remove trailing comma if present

    # replace old explanation block with the fixed one
    new_explanation_block = f'"explanation": {{\n    {fixed_dict}\n  }}'
    fixed_json_str = re.sub(
        r'"explanation"\s*:\s*{[^}]*}', new_explanation_block, json_str, flags=re.DOTALL
    )

    return fixed_json_str


@catch_parse_error
def postprocess_make_problem_summary(response_payload) -> dict:
    response = remove_formatting(response_payload.content)
    parsed = parse_key_values(response)
    if parsed.get("keywords"):
        keywords = [
            k.strip().strip("'").strip('"')
            for k in parsed["keywords"].split(",")
            if k.strip()
        ]
    else:
        keywords = []
    return {"context": parsed.get("context", ""), "keywords": keywords}


def postprocess_callout(msg: str, template: str = "callout_image"):
    msg = "> " + msg.strip().replace("\n", "\n> ")
    template = load_template().get(template, "")
    if template:
        return template.format(text=msg)
    else:
        return msg
