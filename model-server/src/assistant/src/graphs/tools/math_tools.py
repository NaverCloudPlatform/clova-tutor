# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import random
from typing import Optional

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.types import Command, Literal

from assistant.src.hcx_structured_output import PromptToolMessageBundle
from assistant.src.mapping import ResponseStyleMapMath
from assistant.src.schema import ResponseInfo, State, UnknownConcept
from assistant.src.schema.math_tool_schema import (
    ConceptNoteToolArgs,
    DefaultChatToolArgs,
    DetectUnknownConceptMathToolArgs,
    RecommendProblemToolArgs,
    StepwiseSolutionToolArgs,
)
from assistant.src.utils.call_utils import (
    attach_summed_usage,
    concat_messages,
    convert_message_content,
    get_message,
    get_query_with_context,
)


def response_react_agent_math(
    qa_instance, state: State
) -> Command[Literal["finalize_chat"]]:
    """
    next: finalize_chat
    """
    qa_instance.structured_logger.log_node_start(
        "response_react_agent_math",
    )

    # Reset HSO token counter at function start
    qa_instance.call_manager.tool_llm.reset_hso_token_usage()

    tools = create_math_tools(qa_instance, state)
    tool_node = ToolNode(tools)
    state.response_info = getattr(state, "response_info", None) or ResponseInfo()

    # Set tool_prompt_path for response_react_agent to use subject-specific prompt
    # Store tool_prompt_path in instance __dict__ to avoid Pydantic validation
    tool_llm = qa_instance.call_manager.tool_llm
    # Use relative path - will be resolved relative to prompt directory in bind_tools
    tool_llm.__dict__["tool_prompt_path"] = "prompt_tool_call_math.yaml"

    math_react_limit = create_react_agent(tool_llm, tools=tool_node).with_config(
        recursion_limit=10
    )
    state.messages = convert_message_content(state.messages)
    response = math_react_limit.invoke(state)

    messages = attach_summed_usage(response["messages"])

    # Extract return_direct=True tool names from the tools list
    return_direct_tool_names = {
        t.name for t in tools if getattr(t, "return_direct", False)
    }

    # Priority 1: Find ToolMessage from return_direct=True tools
    last = next(
        (
            m
            for m in reversed(messages)
            if isinstance(m, ToolMessage)
            and getattr(m, "name", None) in return_direct_tool_names
        ),
        None,
    )

    # Priority 2: Find AIMessage (LLM generated response)
    if last is None:
        last = next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)),
            None,
        )

    # Priority 3: Fallback to any ToolMessage
    if last is None:
        last = next(
            (m for m in reversed(messages) if isinstance(m, ToolMessage)),
            messages[-1],
        )

    if isinstance(last, ToolMessage):
        # If ToolMessage, convert to AIMessage
        last = AIMessage(
            content=last.content,
            additional_kwargs={"final_response": True},
        )
    state.messages = [last]

    # Get HSO token usage for this function
    hso_usage = qa_instance.call_manager.tool_llm.get_hso_token_usage()

    qa_instance.structured_logger.log_node_end(
        "response_react_agent_math",
        result_summary="Math react agent completed",
        additional_data={"hso_token_usage": hso_usage},
    )

    return Command(
        update=state,
        goto="finalize_chat",
    )


def create_pre_math_tools(qa_instance, state: State):
    _current_state = state

    @tool(
        args_schema=DetectUnknownConceptMathToolArgs,
    )
    def detect_unknown_concept_math_tool():
        state = _current_state if _current_state else state
        qa_instance.structured_logger.log_info("🛠️ detect_unknown_concept_math executed")

        unknown_concept = UnknownConcept(subject=qa_instance.default_subject)

        unknown_list = qa_instance.unknown_concept_db.list_unknown_concepts(
            subject=qa_instance.default_subject
        )

        # Ensure unknown_list is a list
        if not isinstance(unknown_list, list):
            unknown_list = []

        # unit filtering
        if state.subject_info and state.subject_info.unit:
            unknown_list = [
                item
                for item in unknown_list
                if isinstance(item, dict)
                and item.get("key_concept") == state.subject_info.unit
            ]
        else:
            # If subject_info or unit is None, filter out invalid items
            unknown_list = [item for item in unknown_list if isinstance(item, dict)]

        last_ai_message = get_message(state, message_type=AIMessage, idx=-1)
        idx = -2 if last_ai_message.additional_kwargs.get("confirm_transition") else -1
        if state.problem_history:
            messages = state.messages[1:idx]
        else:
            messages = state.messages[:idx]

        info = qa_instance.call_manager.invoke(
            "eduqa_math/detect_unknown_concept_math",
            {"messages": messages, "unknown_concept": unknown_list},
        )
        if info:
            info.setdefault("subject", qa_instance.default_subject)
            if state.subject_info and state.subject_info.unit:
                info.setdefault("key_concept", state.subject_info.unit)
            unknown_concept = UnknownConcept(**info)
            if unknown_concept.unknown_concept:
                qa_instance.unknown_concept_db.upsert_unknown_concept(
                    subject=qa_instance.default_subject,
                    key_concept=unknown_concept.key_concept,
                    unknown_concept=", ".join(unknown_concept.unknown_concept),
                    unknown_concept_reason=unknown_concept.unknown_concept_reason,
                )
                qa_instance.structured_logger.log_info(
                    "detect_unknown_concept_math: unknown concept detected",
                    {
                        "unknown_concepts": unknown_concept,
                    },
                )
            else:
                qa_instance.unknown_concept_db.delete_unknown_concepts(
                    subject=qa_instance.default_subject,
                    key_concept=unknown_concept.key_concept,
                )
                qa_instance.structured_logger.log_info(
                    "detect_unknown_concept_math: unknown concept deleted",
                    {
                        "key_concept": unknown_concept.key_concept,
                    },
                )

        qa_instance.structured_logger.log_node_end(
            "detect_unknown_concept_math",
            result_summary="Unknown concept detection completed",
            additional_data={
                "unknown_list_count": len(unknown_list),
            },
        )
        return

    return [detect_unknown_concept_math_tool]


def create_math_tools(qa_instance, state: State):

    _current_state = state

    @tool(
        args_schema=ConceptNoteToolArgs,
    )
    def concept_note_tool() -> PromptToolMessageBundle:
        state = _current_state if _current_state else state
        state.response_info.response_style.add(ResponseStyleMapMath.MATH_CONCEPT)
        qa_instance.structured_logger.log_info("🛠️ concept_note_tool executed")

        # retrieve_equation
        reference_equations = qa_instance.retrieve(
            "Contents_fig_math",
            get_query_with_context(state.messages, state.problem_info),
        )
        reference_document = reference_equations

        # update response math concept
        prompt_messages = qa_instance.call_manager.generate_prompt(
            "eduqa_math/update_response_math_concept",
            {
                "messages": state.messages,
                "subject_info": state.subject_info,
                "problem_info": state.problem_info,
                "reference_document": reference_document,
                "student_profile": qa_instance.student_profile,
            },
        )
        state.reference_document = reference_document
        return concat_messages(prompt_messages)

    @tool(
        args_schema=StepwiseSolutionToolArgs,
    )
    def stepwise_solution_tool() -> PromptToolMessageBundle:
        state = _current_state if _current_state else state
        state.response_info.response_style.add(ResponseStyleMapMath.STEPWISE_SOLUTION)
        qa_instance.structured_logger.log_info(
            "🛠️ stepwise_solution_tool executed",
            additional_data={
                "problem_info": state.problem_info,
            },
        )

        prompt_messages = qa_instance.call_manager.generate_prompt(
            "eduqa_math/update_response_stepwise_solution",
            {
                "messages": state.messages,
                "problem_info": state.problem_info,
                "student_profile": qa_instance.student_profile,
            },
        )
        return concat_messages(prompt_messages)

    @tool(args_schema=RecommendProblemToolArgs, return_direct=True)
    def recommend_problem_tool(
        correct_answer: Optional[bool] = None,
        more_difficult: Optional[bool] = None,
    ):
        state = _current_state
        qa_instance.structured_logger.log_info("🛠️ recommend_problem_tool executed")
        state.response_info.more_difficult = more_difficult

        from assistant.src.graphs.node.common_node import update_recommend_problem

        response_info = update_recommend_problem(qa_instance, state)
        state.response_info = response_info
        state.response_info.response_style.add(ResponseStyleMapMath.RECOMMEND_PROBLEM)
        qa_instance.graph.update_state(
            qa_instance.thread_config,
            {
                "response_info": state.response_info,
                "recommended_problem_ids": state.recommended_problem_ids,
            },
        )

        if response_info.recommend_problem:
            content = qa_instance.message_templates["user_want_problem"].format(
                section=state.subject_info.section
            )
            has_recommendation = True
        else:
            # Choose message based on the reason for no problems
            if response_info.no_problems_reason == "no_data":
                # vectordb에 해당 단원 문제가 아예 없는 경우
                content = qa_instance.message_templates["no_problems_available"]
            elif response_info.no_problems_reason == "all_solved":
                # 문제를 풀고 나서 더 이상 추천할 문제가 없는 경우
                content = qa_instance.message_templates["not_have_recommend_problem"]
            else:  # all_recommended
                # 문제를 풀지 않고 추천만 받았는데 더 이상 추천할 문제가 없는 경우
                content = qa_instance.message_templates["no_more_recommendations"]
            has_recommendation = False
        qa_instance.structured_logger.log_info(
            "update_response_recommend_problem_math completed",
            {
                "has_recommendation": has_recommendation,
                "response_info": state.response_info,
                "correct_answer": correct_answer,
                "more_difficult": more_difficult,
            },
        )
        if correct_answer:
            feedback_template = qa_instance.message_templates[
                "feedback_answer_for_correct_answer"
            ]
            feedback_subset = [
                line.strip()
                for line in feedback_template.strip().split("\n")
                if line.strip()
            ]
            feedback = random.choice(feedback_subset)
            return feedback + " " + content
        return content

    @tool(
        args_schema=DefaultChatToolArgs,
    )
    def default_chat_tool() -> PromptToolMessageBundle:
        state = _current_state if _current_state else state
        state.response_info.response_style.add(ResponseStyleMapMath.DEFAULT_CHAT)
        # Simple node - log_info only
        current_subject = (
            state.subject_info.subject
            if state.subject_info and state.subject_info.subject
            else None
        )

        qa_instance.structured_logger.log_info("🛠️ default_chat executed")

        if qa_instance.default_subject == current_subject:
            prompt_name = f"eduqa_{qa_instance.subject_eng_name}/default_chat_{qa_instance.subject_eng_name}"
        else:
            prompt_name = f"eduqa_{qa_instance.subject_eng_name}/default_chat_others"

        prompt_messages = qa_instance.call_manager.generate_prompt(
            prompt_name,
            {
                "messages": state.messages,
                "problem_info": state.problem_info,
                "student_profile": qa_instance.student_profile,
            },
        )

        return concat_messages(prompt_messages)

    return [
        concept_note_tool,
        stepwise_solution_tool,
        recommend_problem_tool,
        default_chat_tool,
    ]
