# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import re

import json_repair

from assistant.src.post_process.common_post_process import (
    parse_key_values,
    remove_formatting,
    remove_template,
)
from assistant.src.schema import SubjectInfo
from assistant.src.utils.call_utils import catch_parse_error
from assistant.src.utils.data_utils import convert_to_json_compatible_str, load_data

MATH_section = load_data("opensource_math_course.csv")


@catch_parse_error
def postprocess_update_subject_info_math(response_payload: str):
    def extract_section_and_unit(input_str: str) -> str:
        # Extract section from the value (e.g., "1-2. 수와 연산")
        # grade < 10인 경우, 모델이 예측한 section 값은 실제로 unit을 의미하므로
        # "학년-번호"(예: 3-2)에 해당하는 section과 unit을 함께 찾아서 반환한다.
        section_matches = re.search(r"(\d+-\d+)\.\s*(.*)", input_str)
        if section_matches:
            num_value = section_matches.group(1)
            grade, section_order = num_value.split("-")
            grade, section_order = int(grade.strip()), int(section_order.strip())

            # 학년별로 정렬 기준 컬럼 선택: 10 미만이면 unit, 10 이상이면 section
            section_from_num = MATH_section[MATH_section["normalized_grade"] == grade]
            key = "unit" if grade < 10 else "section"

            if not section_from_num.empty:
                section_from_num = section_from_num.drop_duplicates(subset=[key])

            if (not section_from_num.empty) and (
                len(section_from_num) >= section_order
            ):
                section_from_num = section_from_num.iloc[section_order - 1].section
            else:
                section_from_num = None

            section_from_str = section_matches.group(2).strip()

            # If the section from the number does not match the section from the string,
            if section_from_num != section_from_str:
                # Check if the section from the string is in the MATH_section
                if (
                    section_from_str in MATH_section["section"].values
                    or section_from_num is None
                ):
                    return section_from_str, None
                # If it is not, use the section from the number
                else:
                    # grade < 10
                    return section_from_num, section_from_str
            else:
                return section_from_str, None

        # If no match, use the original value
        else:
            return input_str, None

    # using basic chain
    response = response_payload.content
    response = remove_template(response)
    subject_info = response.split("\n")
    response = {}
    for info in subject_info:
        info = info.strip()
        if not info or ":" not in info:
            continue
        parts = info.split(":", 1)  # 최대 1번만 split
        key, value = parts
        key, value = key.strip(), value.strip()
        if not key:
            continue
        if key == "section":
            value, unit_if_grade_under_10 = extract_section_and_unit(value)

        if key == "unit" and unit_if_grade_under_10:
            response[key] = unit_if_grade_under_10
        else:
            response[key] = value

    if "topic" in response:
        response["topic"] = [s.strip() for s in response["topic"].split(",")]

    if not response:
        return None, None
    response["is_generated"] = True
    return response, response_payload.usage_metadata


@catch_parse_error
def postprocess_update_problem_info_math(response_payload: str):
    response = response_payload.content
    match = re.search(r"```(?:json|python)?\n(.*?)```", response, re.DOTALL)
    if match:
        parsed = json_repair.loads(
            convert_to_json_compatible_str(match.group(1).strip())
        )
        converted_explanation = {int(k): v for k, v in parsed.items()}
        converted_answer = parsed.get("answer", "")
    else:
        converted_explanation = re.search(
            r"explanation:\s*(.*?)(?:\nanswer:|\Z)", response, re.DOTALL
        )
        converted_answer = re.search(r"answer:\s*(.*)", response, re.DOTALL)

        if converted_explanation:
            explanation_text = converted_explanation.group(1).strip()
            matches = re.findall(
                r"\d+\.\s+(.*?)(?=\n\d+\.|\Z)", explanation_text, re.DOTALL
            )
            if not matches:
                matches = [
                    line.strip()
                    for line in explanation_text.split("\n")
                    if line.strip()
                ]
            converted_explanation = {i + 1: m.strip() for i, m in enumerate(matches)}
        if converted_answer:
            converted_answer = converted_answer.group(1).strip()

    response_dict = {
        "level": None,
        "data_source": None,
        "subject_info": SubjectInfo(subject="수학", is_generated=False),
        "image_url": None,
        "explanation": {
            "text": converted_explanation,
            "is_generated": True,
        },
        "answer": {
            "text": converted_answer,
            "is_generated": True,
        },
    }
    return response_dict, response_payload.usage_metadata


@catch_parse_error
def postprocess_update_user_query_info_math(response_payload: str) -> dict:
    response = response_payload.content
    code_block = re.search(r"```(?:json|python)?\s*([\s\S]*?)\s*```", response)
    if code_block:
        content = code_block.group(1)
    else:
        content = response.strip()
    parsed = json_repair.loads(convert_to_json_compatible_str(content))
    return parsed, response_payload.usage_metadata


@catch_parse_error
def postprocess_detect_unknown_concept_math(response_payload) -> dict:
    response = remove_formatting(response_payload.content)
    parsed = parse_key_values(response)
    if parsed.get("unknown_concept"):
        unknown_concept = [k.strip() for k in parsed["unknown_concept"].split(",")]
    else:
        unknown_concept = []
    return {
        "unknown_concept": unknown_concept,
        "unknown_concept_reason": (
            parsed.get("unknown_concept_reason", "") if unknown_concept else ""
        ),
    }
