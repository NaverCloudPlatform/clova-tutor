# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections import defaultdict

from pydantic import BaseModel

from assistant.src.utils.load_utils import load_yaml
from config.config import model_config

tool_docs = {
    "common": load_yaml(model_config.DEFAULT_PROMPT_PATH + "/eduqa_common_tool.yaml")
}
tool_descriptions = {}
tool_args = defaultdict(dict)


def register_tools(doc_name: str, docs: dict, tool_descriptions: dict, tool_args: dict):
    for tool, meta in docs.items():
        desc = meta.get("description")
        args = meta.get("Args")

        tool_key = f"{doc_name}.{tool}"
        if desc:
            tool_descriptions[tool_key] = desc
        if args:
            tool_args[tool_key] = args


for name, docs in tool_docs.items():
    register_tools(name, docs, tool_descriptions, tool_args)

make_problem_summary_tool_desc = tool_descriptions["common.make_problem_summary_tool"]
persuasion_tool_desc = tool_descriptions["common.persuasion_tool"]
problem_info_tool_desc = tool_descriptions["common.problem_info_tool"]


class MakeProblemSummaryToolArgs(BaseModel):
    """{make_problem_summary_tool_desc}"""


MakeProblemSummaryToolArgs.__doc__ = make_problem_summary_tool_desc


class PersuasionToolArgs(BaseModel):
    """{persuasion_tool_desc}"""


PersuasionToolArgs.__doc__ = persuasion_tool_desc


class ProblemInfoToolArgs(BaseModel):
    """{problem_info_tool_desc}"""


ProblemInfoToolArgs.__doc__ = problem_info_tool_desc
