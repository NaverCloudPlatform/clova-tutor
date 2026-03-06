# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import re
from enum import Enum
from typing import Any, Iterable, Mapping, Optional

from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from assistant.src.utils.call_utils import get_grade_to_str
from assistant.src.utils.load_utils import load_data

MATH_SECTION = load_data("opensource_math_course.csv")
MATH_OBJECTIVES = load_data("opensource_math_learning_objectives.csv")
ENG_GRAMMAR_TOPIC = load_data("grammar_topic.csv")


def to_dict(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return {k: to_dict(v) for k, v in obj.model_dump().items()}

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, Mapping):
        return {k: to_dict(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        iterable: Iterable = (to_dict(i) for i in obj)
        return type(obj)(iterable)

    return obj


def convert_to_json_compatible_str(string):
    return string.replace("None", "null")


def section2grade(section: str, unit: Optional[str] = None):
    if unit:
        grade = MATH_SECTION[
            (MATH_SECTION["section"] == section) & (MATH_SECTION["unit"] == unit)
        ]
    else:
        grade = MATH_SECTION[MATH_SECTION["section"] == section]
    if grade.empty:
        return 0
    else:
        return grade.iloc[0]["grade"]


def is_english(text: str) -> bool:
    if not text:
        return False

    clean_text = re.sub(r"[^\w]", "", text)
    if not clean_text:
        return False

    # 영어 + 숫자 비중이 70% 이상인 경우 영어로 판단
    eng_num_count = len(re.findall(r"[a-zA-Z0-9]", clean_text))
    return eng_num_count / len(clean_text) >= 0.7


def is_korean(text: str) -> bool:
    if not text:
        return False

    clean_text = re.sub(r"[^\w]", "", text)
    if not clean_text:
        return False

    # 한글 + 숫자 + 영문 대문자(고유명사) 비중이 70% 이상이면 한국어로 판단
    kor_num_count = len(re.findall(r"[가-힣ㄱ-ㅎㅏ-ㅣ0-9A-Z]", clean_text))
    return kor_num_count / len(clean_text) >= 0.7


def get_grammar_md_table(categories) -> str:
    grammar1, grammar2 = categories
    jsonl_data = load_data("eng_grammar_markdown.jsonl")

    for data in jsonl_data:
        g1 = data.get("grammar1", "").strip()
        g2 = data.get("grammar2", "").strip()

        if {g1, g2} == {grammar1.strip(), grammar2.strip()}:
            return data.get("markdown", "")
    return ""


def get_sections_for_grade_range(grade: int):
    MATH_SECTION["normalized_grade"] = MATH_SECTION["normalized_grade"].astype(int)

    condition = MATH_SECTION["normalized_grade"].between(
        MATH_SECTION["normalized_grade"].min(), grade
    )
    result = []
    for g in sorted(MATH_SECTION[condition]["normalized_grade"].unique()):
        grade_df = MATH_SECTION[MATH_SECTION["normalized_grade"] == g]

        key = "unit" if g < 10 else "section"
        if key == "unit":
            grade_df = grade_df.drop_duplicates(subset=["unit"])
        else:
            grade_df = grade_df.drop_duplicates(subset=["section"])

        sections = grade_df[key].tolist()
        formatted_sections = "\n".join(
            f"{g}-{j}. {section}" for j, section in enumerate(sections, start=1)
        )
        result.append(f"{g}. {get_grade_to_str(g)}\n{formatted_sections}")
    return "\n\n".join(result)


def get_grammar_topic():
    return ", ".join(ENG_GRAMMAR_TOPIC["grammar_topic"].to_list())


def get_objectives_for_grade(grade: int):
    condition = MATH_OBJECTIVES["grade"].str.contains(str(grade))
    current_objectives = MATH_OBJECTIVES[condition]

    result = ""
    for i, section in enumerate(current_objectives["section"].unique(), start=1):
        result += f"{i}. {section}\n"

        for j, unit in enumerate(
            current_objectives[current_objectives["section"] == section][
                "unit"
            ].unique(),
            start=1,
        ):
            objectives = current_objectives[
                (current_objectives["section"] == section)
                & (current_objectives["unit"] == unit)
            ]["objectives"].tolist()
            formatted_objectives = "\n".join(
                f"    - {objective}" for objective in objectives
            )
            result += f"  {i}-{j}. {unit}\n{formatted_objectives}\n"

    return result


def format_messages(messages, idx=-1):
    result = []
    seq = messages if (idx is None or idx == -1) else messages[:idx]
    for m in seq:
        if isinstance(m, HumanMessage):
            label = "사용자"
        elif isinstance(m, AIMessage):
            label = "클로바"
        else:
            label = "기타"

        c = m.content
        if isinstance(c, str):
            text = c
        elif isinstance(c, list):
            text = " ".join(
                x.get("content", "") if isinstance(x, dict) else str(x) for x in c
            )
        else:
            text = str(c)

        result.append(f"{label}:\n{text}")
    return "\n\n".join(result)


def build_table_output(grammar_tables: list[str], voca_tables: list[str]) -> str:
    parts = []
    if grammar_tables:
        grammar_str = "\n".join(grammar_tables)
        parts.append(f"활용할 수 있는 문법 비교 표:\n{grammar_str}")

    if voca_tables:
        voca_str = "\n".join(voca_tables)
        parts.append(f"활용할 수 있는 단어 표:\n{voca_str}")

    if not parts:
        return "가지고 있는 표 정보가 없습니다."
    return "\n\n".join(parts) if parts else ""


def _extract_text_from_content(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                val = part.get("content") or part.get("text")
                if isinstance(val, str) and val.strip():
                    return val.strip()
    return ""
