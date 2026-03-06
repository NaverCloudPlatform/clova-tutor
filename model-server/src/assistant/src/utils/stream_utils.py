# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import sys
import traceback
from typing import TYPE_CHECKING

from assistant.src.mapping import ErrorType, ResponseStyleMapEng
from assistant.src.post_process.common_post_process import (
    postprocess_callout,
    postprocess_streaming_message,
)
from assistant.src.schema import Error, State
from assistant.src.utils.call_utils import get_image_message

if TYPE_CHECKING:
    from assistant.src.models.base import EduQA


class AgentStreamHandler:
    def __init__(self, qa_instance: "EduQA"):
        self.qa_instance = qa_instance

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return getattr(self.qa_instance, name)

    def _init_streaming_state(self):
        """Initialize streaming state variables."""
        return {
            "is_first": True,
            "wait": False,
            "response_buffer": "",
            "wait_tag": False,
            "response_buffer_tag": "",
            "wrap_response": False,
        }

    def _should_wrap_response(self, node, curr_state, streaming_state):
        """Check if response should be wrapped due to image parse failure."""
        error_obj = curr_state.get("error", None)
        if isinstance(error_obj, Error):
            error_type = error_obj.type
        elif isinstance(error_obj, dict):
            error_type = error_obj.get("type")
        else:
            error_type = None
        return (
            node in self.image_parse_failure_nodes
            and error_type == ErrorType.PARSE
            and not streaming_state["wrap_response"]
            and get_image_message(curr_state["messages"][-1])
        )

    async def _handle_end_message(self, msg, node, curr_state, streaming_state):
        """Handle end message from terminal nodes."""
        if node in self.image_parse_failure_nodes and streaming_state["wrap_response"]:
            wrapped_response = postprocess_callout(msg.content[-1]["content"])
            curr_state["model_response"] = wrapped_response
            yield State(**curr_state)
            streaming_state["wrap_response"] = False

    async def _handle_non_streaming_node(self, msg, curr_state, streaming_state):
        """Handle non-streaming terminal nodes."""
        if streaming_state["wrap_response"]:
            return
        curr_state["model_response"] = msg.content[-1]["content"]
        yield State(**curr_state)

    async def _handle_table_insertion(self, state):
        """Handle table insertion for vocabulary or grammar sections."""
        section = state["subject_info"].section if state["subject_info"] else None
        table = []
        if section == "단어":
            table = state["table_response"] or []
        elif section == "문법":
            table = [state["table_response"]] or []

        state["model_response"] = "\n" + "\n".join(table)
        yield State(**state)

    async def _handle_streaming_node(self, msg, curr_state, streaming_state):
        """Handle streaming terminal nodes."""
        state = curr_state

        (
            msg,
            streaming_state["is_first"],
            streaming_state["wait"],
            streaming_state["response_buffer"],
            skip,
        ) = postprocess_streaming_message(
            msg,
            streaming_state["is_first"],
            streaming_state["wait"],
            streaming_state["response_buffer"],
        )
        if skip:
            return

        if streaming_state["wait_tag"] or streaming_state["wrap_response"]:
            return

        state["model_response"] = msg.content
        yield State(**state)

    async def _handle_terminal_node(self, msg, node, curr_state, streaming_state):
        """Handle messages from terminal nodes."""
        human_msg = curr_state["messages"][-1]
        ai_msg = msg
        is_end = msg.additional_kwargs.get("type", "streaming") == "end"

        if node in self.non_streaming_nodes:
            if is_end:
                self.save_chat_message(human_msg, ai_msg)
                async for state in self._handle_non_streaming_node(
                    msg, curr_state, streaming_state
                ):
                    yield state
            return
        elif is_end:
            self.save_chat_message(human_msg, ai_msg)
            async for state in self._handle_end_message(
                msg, node, curr_state, streaming_state
            ):
                yield state
        else:
            if node == "agent":  # if react node
                if msg.additional_kwargs.get("final_response", None):
                    async for state in self._handle_streaming_node(
                        msg, curr_state, streaming_state
                    ):
                        yield state
            else:  # else etc. (ex. default_chat)
                async for state in self._handle_streaming_node(
                    msg, curr_state, streaming_state
                ):
                    yield state

    def _get_reference_problems_ids(self, reference_problems):
        if reference_problems:
            return {
                level: [
                    p["problem_info"]["problem_id"]
                    for p in reference_problems.get(level)
                ]
                for level in ("easy", "normal", "hard")
            }
        return None

    def _get_state_changes(self, old_state, new_state):
        """Compare two states and return only the changed fields."""
        if not isinstance(old_state, State):
            old_state = State(**old_state)
        if not isinstance(new_state, State):
            new_state = State(**new_state)

        old_dict = old_state.model_dump()
        new_dict = new_state.model_dump()

        changes = {}
        for key, new_value in new_dict.items():
            if key == "model_response":
                continue

            if key == "reference_problems":
                new_value = self._get_reference_problems_ids(new_value)
                old_value = self._get_reference_problems_ids(old_dict.get(key))
            else:
                old_value = old_dict.get(key)

            if old_value != new_value:
                changes[key] = {"old": old_value, "new": new_value}

        return changes

    def _handle_non_terminal_node(self, state, curr_state):
        """Handle non-terminal nodes."""
        if not isinstance(state, State):
            state = State(**state)

        new_state = State(**curr_state)
        if state != new_state:
            changes = self._get_state_changes(state, new_state)
            if changes:  # Only log if there are actual changes
                for field, change in changes.items():
                    self.structured_logger.log_state_change(
                        field=field,
                        old_value=change["old"],
                        new_value=change["new"],
                        change_reason="State update during node execution",
                    )
            state = new_state
        return state

    async def _handle_recommendation(self, curr_state, prev_langgraph_node):
        """Handle recommendation tool responses."""

        # TODO prev_langgraph_node logic 수정 (update_response_completion_feedback_eng, update_response_completion_feedback_math 사용 x)
        if prev_langgraph_node in {
            "update_response_completion_feedback_math",
            "update_response_completion_feedback_eng",
        }:
            if not curr_state["response_info"].recommend_problem:
                recommend_response = self.message_templates[
                    "not_have_recommend_problem"
                ]
            else:
                recommend_response = self.message_templates["user_solve_problem"]
            curr_state["model_response"] = "\n" + recommend_response
            yield State(**curr_state)

    async def _handle_translation(self, curr_state):
        """Handle recommendation tool responses."""
        response_info = curr_state.get("response_info")
        if not response_info or self.qa_instance.default_subject == "수학":
            return
        if (
            ResponseStyleMapEng.TRANSLATION not in response_info.response_style
            or not curr_state.get("translation_response")
        ):
            return
        curr_state["model_response"] = "\n\n" + postprocess_callout(
            curr_state.get("translation_response"), "callout_translation"
        )

        yield State(**curr_state)

    async def _handle_table(self, curr_state):
        """Handle recommendation tool responses."""
        response_info = curr_state.get("response_info")
        if not response_info or self.qa_instance.default_subject == "수학":
            return
        if (
            ResponseStyleMapEng.TABLE_FETCH not in response_info.response_style
            or not curr_state.get("table_response")
        ):
            return
        curr_state["model_response"] = "\n\n" + postprocess_callout(
            "\n".join(curr_state.get("table_response")), "callout_table"
        )
        yield State(**curr_state)

    async def _handle_error(self, e):
        """Handle exceptions and yield error state."""
        tb = sys.exc_info()[2]
        traceback_info = traceback.extract_tb(tb)[-1]
        filename, line, _, _ = traceback_info
        filename = filename.split("/")[-1]

        error_info = {
            "type": e.error_type if hasattr(e, "error_type") else ErrorType.UNKNOWN,
            "error_msg": str(e),
            "node_name": e.node_name if hasattr(e, "node_name") else "",
            "filename": filename,
            "line": line,
            "model_param": self.call_manager.model_param,
        }

        self.structured_logger.log_error(
            error_type=error_info["type"],
            error_msg=error_info["error_msg"],
            node_name=error_info.get("node_name"),
            filename=error_info.get("filename"),
            line=error_info.get("line"),
            model_param=error_info.get("model_param"),
        )

        self.graph.update_state(
            self.thread_config,
            {
                "error": error_info,
                "model_response": self.message_templates["say_cannot_understand"],
            },
        )
        yield State(**self.graph.get_state(self.thread_config).values)

    async def astream(self, state: State):
        try:
            streaming_state = self._init_streaming_state()
            prev_langgraph_node = None
            async for _, mode, chunk in self.graph.astream(
                state,
                config=self.thread_config,
                stream_mode=["messages", "updates"],
                subgraphs=True,
            ):
                curr_state = self.graph.get_state(self.thread_config).values
                if mode == "messages":
                    msg, node = chunk[0], chunk[1]["langgraph_node"]
                    # skip background nodes
                    if node in self.background_nodes:
                        continue

                    # check whether image parse failed to wrap response
                    if self._should_wrap_response(node, curr_state, streaming_state):
                        streaming_state["wrap_response"] = True

                    if node in self.terminal_nodes and msg.content:
                        async for state in self._handle_terminal_node(
                            msg, node, curr_state, streaming_state
                        ):
                            yield state
                    else:
                        state = self._handle_non_terminal_node(state, curr_state)

                    prev_langgraph_node = (
                        chunk[1]["langgraph_node"]
                        if chunk[1]["langgraph_node"]
                        not in self.extern_state_update_nodes
                        else prev_langgraph_node
                    )

                elif mode == "updates":
                    for node in self.extern_state_update_nodes:
                        if node in chunk:
                            async for state in self._handle_translation(curr_state):
                                yield state
                            async for state in self._handle_table(curr_state):
                                yield state
                            async for state in self._handle_recommendation(
                                curr_state, prev_langgraph_node
                            ):
                                yield state

        except Exception as e:
            async for state in self._handle_error(e):
                yield state
