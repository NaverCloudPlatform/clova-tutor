# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
import re

import json_repair

from assistant.src.mapping import ResponseStyleMapEng
from assistant.src.post_process.common_post_process import (
    fix_explanation,
    parse_key_values,
    remove_formatting,
)
from assistant.src.schema import SubjectInfo
from assistant.src.utils.call_utils import catch_parse_error
from assistant.src.utils.data_utils import (
    convert_to_json_compatible_str,
    is_english,
    is_korean,
)


@catch_parse_error
def postprocess_update_subject_info_eng(response_payload: str):
    response = response_payload.content
    response = remove_formatting(response)
    items = parse_key_values(response)

    parsed = {}
    for key, value in items.items():
        if key == "subject":
            parsed[key] = value.replace("그 외", "기타")
        elif key == "topic":
            parsed[key] = [
                v.strip().lower()
                for v in value.strip().split(",")
                if v.strip() and v.strip().strip('"')
            ]
        else:
            parsed[key] = value
    if not parsed:
        return None, None
    parsed["is_generated"] = True
    return parsed, response_payload.usage_metadata


@catch_parse_error
def postprocess_update_problem_info_eng(response_payload: str):
    response_dict = {
        "level": None,
        "data_source": None,
        "subject_info": SubjectInfo(subject="영어", is_generated=False),
        "image_url": None,
    }
    response = response_payload.content
    code_block = re.search(r"```(?:json|python)?\s*([\s\S]*?)\s*```", response)
    if code_block:
        content = code_block.group(1)
    else:
        content = response.strip()

    content = fix_explanation(content)
    try:
        response = json_repair.loads(convert_to_json_compatible_str(content))
    except Exception as e:
        raise ValueError(
            f"Failed to parse JSON response. "
            f"Error: {e}. "
            f"Content: {content[:500]}..."
        )
    if not isinstance(response, dict):
        raise ValueError(
            f"Parsed response is not a dict, got {type(response)}. "
            f"Response: {response}"
        )

    explanation = response.get("explanation", {})
    if isinstance(explanation, dict):
        explanation = {int(k): v for k, v in explanation.items()}
    elif isinstance(explanation, list):
        explanation = {i + 1: v for i, v in enumerate(explanation)}
    else:
        raise ValueError(f"Invalid explanation format: {explanation}")

    answer = response.get("answer", "")
    question = (
        f"{response.get('contents')}\n{response.get('question')}"
        if response.get("contents")
        else response.get("question")
    )
    response_dict.update(
        {
            "question": question,
            "explanation": {"text": explanation, "is_generated": True},
            "answer": {"text": answer, "is_generated": True},
        }
    )
    return response_dict, response_payload.usage_metadata


@catch_parse_error
def postprocess_update_user_query_info_eng(response_payload: str) -> dict:
    def safe_int(parsed: dict, key: str) -> int | None:
        value = parsed.get(key, "")
        return int(value[0]) if value and value[0].isdigit() else None

    content = remove_formatting(response_payload.content)
    parsed = parse_key_values(content)

    return {
        "query_evaluation": safe_int(parsed, "query_evaluation"),
        "learning_phase": safe_int(parsed, "learning_phase"),
        "more_difficult": (
            parsed.get("more_difficult", "").strip().lower() == "true"
            if parsed.get("more_difficult") is not None
            else None
        ),
    }, response_payload.usage_metadata


@catch_parse_error
def postprocess_update_response_info_eng(response_payload: str) -> dict:
    response = response_payload.content
    response = remove_formatting(response)
    parsed = parse_key_values(response)

    response_style_raw = parsed.get("response_style", "").strip()
    more_difficult_raw = parsed.get("more_difficult")
    response_style = int(response_style_raw) if response_style_raw.isdigit() else None
    more_difficult = (
        more_difficult_raw.strip().lower() == "true"
        if more_difficult_raw
        and response_style == ResponseStyleMapEng.RECOMMEND_PROBLEM
        else None
    )

    voca_additional_raw = parsed.get("response_style_voca_additional")
    response_style_voca_additional = {}
    if voca_additional_raw:
        items = re.split(r";|,(?=\s*[a-zA-Z])", voca_additional_raw)
        for item in items:
            if "=" in item:
                key, value = item.split("=", 1)
                nums = [int(x.strip()) for x in value.split(",") if x.strip().isdigit()]
                response_style_voca_additional[key.strip()] = nums

    return {
        "response_style": response_style,
        "response_style_voca_additional": (
            response_style_voca_additional
            if response_style_voca_additional != {}
            else None
        ),
        "more_difficult": more_difficult,
        "reason": parsed.get("reason", "").strip(),
    }, response_payload.usage_metadata


@catch_parse_error
def postprocess_update_fetch_translation(response_payload: str) -> dict:

    response, usage_metadata = response_payload.content, response_payload.usage_metadata
    response = remove_formatting(response)
    lines = [line.strip() for line in response.split("<split>") if line.strip()]

    # if the response is a single line, split by "/"
    if len(lines) == 1:
        lines = response.strip().split("/")
    content = []
    for line in lines:
        if ":" in line:
            # remove leading "1)", "/:" and trailing "/", '/"', "/'"  if present
            line = re.sub(r"(/\s*:)", ":", line)
            line = re.sub(r"^\s*\d+[\)\.]\s*|(/\s*\")|(/\s*\')", "", line)
            line = line.replace("<split>", "").strip(" /")

            parts = line.split(":", 1)
            en, ko = parts
            en = en.strip()
            ko = ko.strip()

            if en and ko and is_english(en) and is_korean(ko):
                content.append({"en": en, "ko": ko})

    # raise an error if no valid translations are found
    if not content:
        raise ValueError("No valid translations found.")

    result = {"type": "translation", "content": content}

    return (
        f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```",
        usage_metadata,
    )
