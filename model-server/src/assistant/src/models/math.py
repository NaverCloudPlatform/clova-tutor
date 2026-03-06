# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Optional

from langgraph.graph import StateGraph

from assistant.src.graphs.node.common_node import (
    finalize_chat,
    initialize_state,
    update_subject_info,
)
from assistant.src.graphs.tools.math_tools import response_react_agent_math
from assistant.src.mapping import ResponseStyleMapMath
from assistant.src.models.base import EduQA
from assistant.src.schema import ModelParam, StudentProfile


class EduQAMath(EduQA):
    # subgraph
    def __init__(
        self,
        student_profile: StudentProfile,
        model_param: Optional[ModelParam] = None,
        block_advanced_learning: Optional[bool] = False,
        loglevel: str = "DEBUG",
        **kwargs,
    ):
        super().__init__(
            student_profile=student_profile,
            loglevel=loglevel,
            model_param=model_param,
            subject_eng_name="math",
            **kwargs,
        )
        self.default_subject = "수학"
        self.response_style_map = ResponseStyleMapMath

        self.block_advanced_learning = block_advanced_learning
        self.non_streaming_nodes = self.non_streaming_nodes.union(
            {
                "update_response_recommend_problem_math",
            }
        )
        self.graph = self.build_graph()

    def setup_nodes(self, g: StateGraph):
        super().setup_nodes(g)

        def n(name, fn):
            g.add_node(name, lambda state: fn(self, state))

        node_defintions = {
            "initialize_state": initialize_state,
            "response_react_agent": response_react_agent_math,
            "update_subject_info": update_subject_info,
            "finalize_chat": finalize_chat,
        }

        for name, fn in node_defintions.items():
            n(name, fn)
