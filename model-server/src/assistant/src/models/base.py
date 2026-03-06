# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import warnings
from typing import Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from redis.cluster import RedisCluster

from assistant.src.call import CallManager
from assistant.src.client.unknown import UnknownConceptDB
from assistant.src.client.vector import VectorClient
from assistant.src.graphs.node.common_node import (
    default_chat,
    get_problem_info_from_db,
    pre_model_pipeline,
    reject_advanced_learning,
    start_chat,
)
from assistant.src.memory.in_session_memory.redis import RedisMemory
from assistant.src.schema import ModelParam, State, StudentProfile
from assistant.src.utils.load_utils import load_default_prompt, load_template, load_yaml
from assistant.src.utils.logging_utils import set_logger
from assistant.src.utils.stream_utils import AgentStreamHandler
from assistant.src.utils.structured_logger import StructuredLogger

warnings.filterwarnings("ignore", category=DeprecationWarning)


class EduQA:
    def __init__(
        self,
        student_profile: StudentProfile,
        loglevel: str = "DEBUG",
        redis_client: RedisCluster = None,
        subject_eng_name: str = "eng",
        **kwargs,
    ):
        log_filename = kwargs.get("log_filename", "")
        self.logger = self.init_logger(
            loglevel,
            log_filename,
        )

        self.default_subject = ""
        self.subject_eng_name = subject_eng_name
        self.student_profile = student_profile

        # Initialize structured logger after student_profile is set (Use new logging system)
        self.structured_logger = StructuredLogger(
            self.logger, self.student_profile.user_id
        )
        self.message_templates = load_template()
        self.memory = MemorySaver()
        self.thread_config = {
            "configurable": {"thread_id": self.student_profile.user_id}
        }
        self.default_str = load_default_prompt("eduqa_common")
        kwargs_with_thread_id = {**kwargs, "thread_id": self.student_profile.user_id}
        self.call_manager = CallManager(
            self.logger,
            self.default_str[f"formatting_guide_{subject_eng_name}"],
            **kwargs_with_thread_id,
        )

        # initialize db
        self.db = VectorClient(
            base_url=load_yaml("assistant/api_info.yaml")["api-server"][
                "data-server-url"
            ]
        )
        self.unknown_concept_db = UnknownConceptDB(
            base_url=load_yaml("assistant/api_info.yaml")["api-server"][
                "be-server-url"
            ],
            user_id=self.student_profile.user_id,
        )
        self.redis = RedisMemory(redis_client)

        # initialize graph
        self.memory = MemorySaver()

        self.init_node_info()
        self.graph = self.build_graph()

        self.structured_logger.log_info(
            "User profile initialized", {"student_profile": self.student_profile}
        )

    def init_logger(self, loglevel: str, output_filename: str = ""):
        log_level = loglevel.upper()
        if not loglevel in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("Unknown loglevel")
        return set_logger("EduQA", log_level, output_filename)

    def init_node_info(self):
        self.terminal_nodes = {
            "default_chat",
            "response_react_agent",
            "reject_advanced_learning",
            "agent",
        }
        self.non_streaming_nodes = {
            "reject_advanced_learning",
        }
        self.image_parse_failure_nodes = {"default_chat"}
        self.background_nodes = set()
        self.extern_state_update_nodes = {"finalize_chat"}

    def setup_nodes(self, g: StateGraph):
        g.add_node("start_chat", lambda state: start_chat(self, state))
        g.add_node("default_chat", lambda state: default_chat(self, state))
        g.add_node("pre_model_pipeline", lambda state: pre_model_pipeline(self, state))
        g.add_node(
            "get_problem_info_from_db",
            lambda state: get_problem_info_from_db(self, state),
        )
        g.add_node(
            "reject_advanced_learning",
            lambda state: reject_advanced_learning(self, state),
        )

    def extend_edges(self, g: StateGraph):
        pass

    def setup_edges(self, g: StateGraph):
        g.set_entry_point("start_chat")

    def build_graph(self):
        g = StateGraph(State)
        self.setup_nodes(g)
        self.setup_edges(g)
        return g.compile(checkpointer=self.memory)

    def retrieve(
        self,
        index_name: str,
        query: str,
        k: Optional[int] = 2,
        data_filter: Optional[tuple | dict] = None,
    ):
        kwargs = {}
        if data_filter:
            if isinstance(data_filter, tuple):
                filter_property, filter_value = data_filter
                kwargs["filter_property"] = str(filter_property)
                kwargs["filter_value"] = str(filter_value)
            else:
                filters = {}
                for _property, _value in data_filter.items():
                    filters[_property] = str(_value)
                kwargs["all_of_filters"] = filters

            kwargs["search_type"] = "similarity"
        else:
            kwargs["search_type"] = "mmr"

        return self.db.search(
            index_name,
            query,
            k=k,
            **kwargs,
        )

    def save_chat_message(self, human_message, ai_message):
        self.redis.save_to_chat_message(
            self.thread_config["configurable"]["thread_id"],
            human_message,
        )
        self.redis.save_to_in_memory(
            self.thread_config["configurable"]["thread_id"],
            human_message,
        )

        self.redis.save_to_chat_message(
            self.thread_config["configurable"]["thread_id"], ai_message
        )
        self.redis.save_to_in_memory(
            self.thread_config["configurable"]["thread_id"], ai_message
        )

    def save_long_term_memory(self):
        state = State(**self.graph.get_state(self.thread_config).values)
        thread_id = self.thread_config["configurable"]["thread_id"]
        api_info = load_yaml("assistant/api_info.yaml")

        from assistant.src.memory.across_session_memory.memory_system import (
            AgenticMemorySystem,
        )

        with AgenticMemorySystem(api_info) as memory_system:
            memory_system.vector_db.add_profile(self.student_profile)

            for msg in state.messages:
                memory_system.vector_db.add_message(msg, thread_id)

            problem_ids = [
                memory_system.vector_db.add_problem_card(
                    problem_card,
                    thread_id,
                )
                for problem_card in state.problem_history
            ]

            for problem_id in problem_ids:
                memory_system.connect_card(thread_id, problem_id)

    async def astream(self, state: State, model_param: Optional[ModelParam] = None):
        last_message = state.messages[-1]

        # Handle both dict and BaseMessage types
        if isinstance(last_message, dict):
            message_content = last_message.get("content", "")
        else:
            message_content = getattr(last_message, "content", "")

        # Check if message has image
        has_image = False
        if isinstance(message_content, list):
            has_image = any(
                isinstance(block, dict) and block.get("type") in ["image", "image_url"]
                for block in message_content
            )

        self.structured_logger.log_user_query(message_content, has_image=has_image)

        stream_handler = AgentStreamHandler(self)
        async for state in stream_handler.astream(state):
            yield state
