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
from assistant.src.graphs.node.eng_node import reject_listening
from assistant.src.graphs.tools.eng_tools import response_react_agent_eng
from assistant.src.mapping import ResponseStyleMapEng
from assistant.src.models.base import EduQA


class EduQAEng(EduQA):
    def __init__(
        self,
        student_profile,
        model_param=None,
        block_advanced_learning: Optional[bool] = True,
        loglevel: str = "DEBUG",
        **kwargs,
    ):
        super().__init__(
            student_profile=student_profile,
            loglevel=loglevel,
            model_param=model_param,
            subject_eng_name="eng",
            **kwargs,
        )
        self.default_subject = "영어"
        self.block_advanced_learning = block_advanced_learning
        self.response_style_map = ResponseStyleMapEng

        self.terminal_nodes = self.terminal_nodes.union(
            {
                "agent",
                "reject_listening",
            }
        )
        self.non_streaming_nodes = self.non_streaming_nodes.union(
            {
                "reject_listening",
                "update_response_translation",
                "update_response_recommend_problem_eng",
            }
        )
        self.graph = self.build_graph()

    def setup_nodes(self, g: StateGraph):
        super().setup_nodes(g)

        def n(name, fn):
            g.add_node(name, lambda state: fn(self, state))

        node_defintions = {
            "initialize_state": initialize_state,
            "update_subject_info": update_subject_info,
            "response_react_agent": response_react_agent_eng,
            "reject_listening": reject_listening,
            "finalize_chat": finalize_chat,
        }

        for name, fn in node_defintions.items():
            n(name, fn)
