# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections import defaultdict

from pydantic import BaseModel, Field

from assistant.src.schema.common_tool_schema import register_tools
from assistant.src.utils.load_utils import load_yaml
from config.config import model_config

tool_docs = {
    "math": load_yaml(model_config.DEFAULT_PROMPT_PATH + "/eduqa_math_tool.yaml"),
}

tool_descriptions = {}
tool_args = defaultdict(dict)

for name, docs in tool_docs.items():
    register_tools(name, docs, tool_descriptions, tool_args)

# -------------------------------
# math
detect_unknown_concept_math_tool_desc = tool_descriptions[
    "math.detect_unknown_concept_math_tool"
]
concept_note_tool_desc = tool_descriptions["math.concept_note_tool"]

stepwise_solution_tool_desc = tool_descriptions["math.stepwise_solution_tool"]

recommend_problem_tool_desc = tool_descriptions["math.recommend_problem_tool"]
recommend_problem_tool_args = tool_args["math.recommend_problem_tool"]

default_chat_tool_desc = tool_descriptions["math.default_chat_tool"]


class DetectUnknownConceptMathToolArgs(BaseModel):
    """{detect_unknown_concept_math_tool_desc}"""


DetectUnknownConceptMathToolArgs.__doc__ = detect_unknown_concept_math_tool_desc


class ConceptNoteToolArgs(BaseModel):
    """{concept_note_tool_desc}"""


ConceptNoteToolArgs.__doc__ = concept_note_tool_desc


class StepwiseSolutionToolArgs(BaseModel):
    """{stepwise_solution_tool_desc}"""


StepwiseSolutionToolArgs.__doc__ = stepwise_solution_tool_desc


class RecommendProblemToolArgs(BaseModel):
    """{recommend_problem_tool_desc}"""

    correct_answer: bool = Field(
        description=recommend_problem_tool_args["correct_answer"]
    )
    more_difficult: bool = Field(
        description=recommend_problem_tool_args["more_difficult"]
    )


RecommendProblemToolArgs.__doc__ = recommend_problem_tool_desc


class DefaultChatToolArgs(BaseModel):
    """{default_chat_tool_desc}"""


DefaultChatToolArgs.__doc__ = default_chat_tool_desc
