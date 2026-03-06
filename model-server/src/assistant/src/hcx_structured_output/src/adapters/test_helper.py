# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

"""
Test helper for ChatClovaXHSO tool calling tracking.
Provides utilities for collecting and analyzing tool calls during testing.
"""

import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List


def create_tool_calls_tracker(tool_calls_info: List[Dict[str, Any]]) -> Callable:
    """
    Create a tracker function that can be passed to ChatClovaXHSO.tool_calls_tracker.

    This function will be called with tool calls and extract pipeline information
    by analyzing the call stack.

    Args:
        tool_calls_info: List to append tool call information to

    Returns:
        A function that can be set as tool_calls_tracker on ChatClovaXHSO instance
    """

    def tracker(oai_tool_calls: List[Dict[str, Any]]) -> None:
        """
        Track tool calls by analyzing call stack and storing information.

        Args:
            oai_tool_calls: List of OpenAI-format tool calls
        """
        # Determine which pipeline this is from by checking call stack
        stack = traceback.extract_stack()
        pipeline_type = "unknown"
        for frame in stack:
            if "pre_model_pipeline" in frame.filename or "pre_model_pipeline" in str(
                frame
            ):
                pipeline_type = "pre_model_pipeline"
                break
            elif (
                "response_react_agent" in frame.filename
                or "response_react_agent" in str(frame)
            ):
                pipeline_type = "response_react_agent"
                break

        # Warn if pipeline type could not be determined
        if pipeline_type == "unknown":
            print(
                f"⚠️  Warning: Could not determine pipeline type from call stack. "
                f"Tool calls may be incorrectly categorized.",
                flush=True,
            )

        # Store each tool call with metadata
        for tool_call in oai_tool_calls:
            tool_calls_info.append(
                {
                    "tool_name": tool_call["function"]["name"],
                    "tool_args": tool_call["function"]["arguments"],
                    "pipeline_type": pipeline_type,
                    "timestamp": datetime.now().isoformat(),
                    "source": "bind_tools_additional_kwargs",
                }
            )

    return tracker
