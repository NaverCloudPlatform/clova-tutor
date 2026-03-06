# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections import defaultdict
from typing import List, Optional

from pydantic import BaseModel, Field

from assistant.src.schema.common_tool_schema import register_tools
from assistant.src.utils.data_utils import get_grammar_topic
from assistant.src.utils.load_utils import load_yaml
from config.config import model_config

tool_docs = {
    "eng": load_yaml(model_config.DEFAULT_PROMPT_PATH + "/eduqa_eng_tool.yaml"),
}

tool_descriptions = {}
tool_args = defaultdict(dict)


for name, docs in tool_docs.items():
    register_tools(name, docs, tool_descriptions, tool_args)


# -------------------------------
# eng

# 직독직해
translation_tool_desc = tool_descriptions["eng.translation_tool"]
translation_tool_args = tool_args["eng.translation_tool"]

table_fetch_tool_desc = tool_descriptions["eng.table_fetch_tool"]
table_fetch_tool_args = tool_args["eng.table_fetch_tool"]

answer_included_tool_desc = tool_descriptions["eng.answer_included_tool"]

recommend_problem_tool_desc = tool_descriptions["eng.recommend_problem_tool"]
recommend_problem_tool_args = tool_args["eng.recommend_problem_tool"]

default_chat_tool_desc = tool_descriptions["eng.default_chat_tool"]


class SegmentItem(BaseModel):
    """분할된 영어 구문과 해당 한국어 번역 한 쌍"""

    en: str
    ko: str


class TranslationToolArgs(BaseModel):
    """{translation_tool_desc}"""

    text: str = Field(description=translation_tool_args["text"])


TranslationToolArgs.__doc__ = translation_tool_desc


class TableFetchToolArgs(BaseModel):
    """{table_fetch_tool_desc}"""

    voca: Optional[dict[str, List[int]]] = Field(
        default=None, description=table_fetch_tool_args["voca"]
    )

    grammar: Optional[List[str]] = Field(
        default=None,
        description=table_fetch_tool_args["grammar"]["description"].format(
            grammar_topic=get_grammar_topic()
        ),
    )


TableFetchToolArgs.__doc__ = table_fetch_tool_desc


class AnswerIncludedToolArgs(BaseModel):
    """{answer_included_tool_desc}"""


AnswerIncludedToolArgs.__doc__ = answer_included_tool_desc


class RecommendProblemToolArgs(BaseModel):
    """{recommend_problem_tool_desc}"""

    correct_answer: bool = Field(
        default=False, description=recommend_problem_tool_args["correct_answer"]
    )
    more_difficult: bool = Field(
        default=False, description=recommend_problem_tool_args["more_difficult"]
    )


RecommendProblemToolArgs.__doc__ = recommend_problem_tool_desc


class DefaultChatToolArgs(BaseModel):
    """{default_chat_tool_desc}"""


DefaultChatToolArgs.__doc__ = default_chat_tool_desc
