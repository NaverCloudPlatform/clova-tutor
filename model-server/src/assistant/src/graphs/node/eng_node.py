# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from langchain_core.messages import AIMessage
from langgraph.types import Command
from typing_extensions import Literal

from assistant.src.schema import State
from assistant.src.utils.load_utils import load_yaml
from config.config import model_config

common_instruction = load_yaml(model_config.DEFAULT_PROMPT_PATH + "/eduqa_common.yaml")


def reject_listening(qa_instance, state: State) -> Command[Literal["finalize_chat"]]:
    # Error/Edge case - log_node_start only
    qa_instance.structured_logger.log_node_start("reject_listening")
    return Command(
        update={
            "messages": [
                AIMessage(
                    content=[
                        {
                            "type": "text",
                            "content": qa_instance.message_templates[
                                "reject_listening"
                            ],
                        }
                    ],
                    additional_kwargs={"type": "end"},
                )
            ],
        },
        goto="finalize_chat",
    )
