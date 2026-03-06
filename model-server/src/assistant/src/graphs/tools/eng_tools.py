# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
import random
from typing import List, Optional

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.types import Command, Literal

from assistant.src.hcx_structured_output import PromptToolMessageBundle
from assistant.src.hcx_structured_output.src.schemas.primitives import Segments
from assistant.src.hcx_structured_output.src.utils.constants import (
    TRANSLATION_PROMPT_TEMPLATE,
)
from assistant.src.hcx_structured_output.src.utils.load_utils import load_prompt_yaml
from assistant.src.mapping import ResponseStyleMapEng
from assistant.src.schema import ResponseInfo, State
from assistant.src.schema.eng_tool_schema import (
    AnswerIncludedToolArgs,
    DefaultChatToolArgs,
    RecommendProblemToolArgs,
    TableFetchToolArgs,
    TranslationToolArgs,
)
from assistant.src.utils.call_utils import (
    attach_summed_usage,
    concat_messages,
    convert_message_content,
)
from assistant.src.utils.content_utils import generate_markdown
from assistant.src.utils.data_utils import build_table_output, get_grammar_md_table
from assistant.src.utils.load_utils import load_voca, load_yaml
from config.config import model_config

eng_voca_integrated = load_voca()
common_instruction = load_yaml(model_config.DEFAULT_PROMPT_PATH + "/eduqa_common.yaml")


def response_react_agent_eng(
    qa_instance, state: State
) -> Command[Literal["finalize_chat"]]:
    """
    next: finalize_chat
    """
    qa_instance.structured_logger.log_node_start(
        "response_react_agent_eng",
    )

    # Reset HSO token counter at function start
    qa_instance.call_manager.tool_llm.reset_hso_token_usage()

    tools = create_eng_tools(qa_instance, state)
    tool_node = ToolNode(tools)
    state.response_info = getattr(state, "response_info", None) or ResponseInfo()

    # Set tool_prompt_path for response_react_agent to use subject-specific prompt
    # Store tool_prompt_path in instance __dict__ to avoid Pydantic validation
    tool_llm = qa_instance.call_manager.tool_llm
    # Use relative path - will be resolved relative to prompt directory in bind_tools
    tool_llm.__dict__["tool_prompt_path"] = "prompt_tool_call_eng.yaml"

    english_react_limit = create_react_agent(tool_llm, tools=tool_node).with_config(
        recursion_limit=10
    )
    state.messages = convert_message_content(state.messages)
    response = english_react_limit.invoke(state)

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
        "response_react_agent_eng",
        result_summary="English react agent completed, proceeding to finalize_chat",
        additional_data={"hso_token_usage": hso_usage},
    )
    return Command(update=state, goto="finalize_chat")


def create_eng_tools(qa_instance, state: State):

    _current_state = state

    @tool(args_schema=TranslationToolArgs)
    def translation_tool(text) -> PromptToolMessageBundle:
        if not text:
            # temp fallback
            return "사용자가 입력한 문장을 이해하지 못했습니다. 다시 한번 입력해주세요."

        if not getattr(state, "response_info", None):
            state.response_info = ResponseInfo()
        state.response_info.response_style.add(ResponseStyleMapEng.TRANSLATION)
        qa_instance.structured_logger.log_info(
            " 🛠️ update_response_translation_tool executed"
        )
        formatting_guide = common_instruction["formatting_guide_eng"]

        # HSO Module
        system_rules, fewshots = load_prompt_yaml(
            model_config.HSO_PROMPT_PATH + "/prompt_translation.yaml"
        )
        user_text = TRANSLATION_PROMPT_TEMPLATE + f"텍스트:\n{text}"
        user_content = {
            "role": "user",
            "content": [{"type": "text", "text": user_text}],
        }

        hso_instance = qa_instance.call_manager.tool_llm.with_structured_output(
            schema=Segments,
            system_rules=system_rules,
            fewshots=fewshots,
        )
        response = hso_instance.invoke(user_content)
        segments = response.get("parsed", {}).get("segments", [])

        json_callout = (
            "```json\n"
            + json.dumps(
                {"type": "translation", "content": segments},
                ensure_ascii=False,
                indent=2,
            )
            + "\n```"
        )
        state.translation_response = json_callout

        translation_info = "직독직해 결과:\n" + "\n".join(
            f"{s['en']} → {s['ko']}" for s in segments
        )
        prompt = PromptToolMessageBundle(
            system=formatting_guide, reference=translation_info
        )

        qa_instance.structured_logger.log_info(
            "update_fetch_translation", {"has_response": state.translation_response}
        )
        return prompt

    @tool(args_schema=TableFetchToolArgs)
    def table_fetch_tool(
        voca: Optional[dict[str, List[int]]] = None,
        grammar: Optional[List[str]] = None,
    ) -> PromptToolMessageBundle:
        qa_instance.structured_logger.log_info(
            " 🛠️ update_response_table_fetch_tool executed"
        )
        formatting_guide = common_instruction["formatting_guide_eng"]
        state.response_info.response_style.add(ResponseStyleMapEng.TABLE_FETCH)
        # TODO: subject_info.section으로 변경
        if voca:
            state.response_info.eng_table_info.add("단어")
        if grammar:
            state.response_info.eng_table_info.add("문법")
        grammar_tables: list[str] = []
        voca_tables: list[str] = []

        # grammar
        if grammar and len(grammar) == 2:
            table_response = get_grammar_md_table(grammar)
            if table_response:
                grammar_tables.append(table_response)
                qa_instance.structured_logger.log_node_end(
                    "update_fetch_grammar",
                    result_summary="Grammar comparison data prepared for rendering",
                    additional_data={
                        "requested_grammars": grammar,
                    },
                )
            else:
                qa_instance.structured_logger.log_warning(
                    "update_fetch_grammar: fetch failed",
                    {"grammar": grammar},
                )
        else:
            qa_instance.structured_logger.log_node_end(
                "update_fetch_grammar",
                result_summary="No grammar comparison data to process",
            )

        # voca
        if voca:
            voca_in_query = list(voca.keys())
            # Build a list of markdown tables to be rendered by streaming handler
            # Map additional codes to content types
            search_key = {
                0: "voca_basic",
                1: "voca_synonym",
                2: "voca_antonym",
                3: "voca_origin",
                4: "voca_inflection",
                5: "voca_idiom",
            }

            for voca_key in voca_in_query:
                voca_data = next(
                    (
                        item
                        for item in eng_voca_integrated
                        if item.get("word") == voca_key.lower()
                    ),
                    None,
                )
                if not voca_data:
                    qa_instance.structured_logger.log_warning(
                        "update_fetch_voca: fetch failed", {"voca": voca_key}
                    )
                    qa_instance.structured_logger.log_node_end(
                        "update_fetch_voca",
                        result_summary="Failed to fetch vocabulary data",
                        additional_data={"failed_word": voca_key},
                    )
                    continue

                style_codes = voca[voca_key]
                # Validate codes
                if not all(code in search_key for code in style_codes):
                    qa_instance.structured_logger.log_warning(
                        "update_fetch_voca: invalid additional style codes",
                        {"voca": voca_key, "style_codes": style_codes},
                    )
                    qa_instance.structured_logger.log_node_end(
                        "update_fetch_voca",
                        result_summary="Failed due to invalid response styles",
                    )
                    continue
                for code in style_codes:
                    markdown_table = generate_markdown(
                        source=voca_data, content_type=search_key[code]
                    )
                    if markdown_table:
                        voca_tables.append(markdown_table)

                if voca_tables:
                    qa_instance.structured_logger.log_node_end(
                        "update_fetch_voca",
                        result_summary="Voca data prepared for rendering",
                        additional_data={
                            "requested_voca": voca_key,
                        },
                    )
        else:
            qa_instance.structured_logger.log_node_end(
                "update_fetch_voca",
                result_summary="No vocabulary words to process",
            )
        if grammar_tables or voca_tables:
            state.table_response = grammar_tables + voca_tables
            prompt = PromptToolMessageBundle(
                system=formatting_guide,
                reference=build_table_output(grammar_tables, voca_tables),
            )
            return prompt
        else:
            prompt_key = []
            if voca:
                prompt_key.append("update_response_voca")
            if grammar:
                prompt_key.append("update_response_grammar")

            if not prompt_key:
                return ""
            else:
                prompt_messages = []
                for key in prompt_key:
                    prompt_messages += qa_instance.call_manager.generate_prompt(
                        f"eduqa_eng/{key}",
                        {
                            "messages": state.messages,
                            "student_profile": qa_instance.student_profile,
                            "grade": str(qa_instance.student_profile.grade),
                        },
                    )
                return concat_messages(prompt_messages)

    @tool(args_schema=AnswerIncludedToolArgs)
    def answer_included_tool() -> PromptToolMessageBundle:
        qa_instance.structured_logger.log_info(
            " 🛠️ update_response_answer_included executed"
        )
        state.response_info.response_style.add(ResponseStyleMapEng.ANSWER_INCLUDED)
        prompt_messages = qa_instance.call_manager.generate_prompt(
            "eduqa_eng/update_response_answer_included",
            {
                "messages": state.messages,
                "student_profile": qa_instance.student_profile,
                "problem_info": state.problem_info,
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
        state.response_info.response_style.add(ResponseStyleMapEng.RECOMMEND_PROBLEM)
        qa_instance.graph.update_state(
            qa_instance.thread_config,
            {
                "response_info": state.response_info,
                "recommended_problem_ids": state.recommended_problem_ids,
            },
        )

        topics = state.subject_info.topic or []
        topics = [topic.strip() for topic in topics if topic.strip() != "추천"]
        if response_info.recommend_problem:
            if not any(c.strip() for c in topics):
                # case 1-1. cold start recommendation
                content = qa_instance.message_templates[
                    "cold_start_recommendation_eng"
                ].format(section=state.subject_info.section or "")
            else:
                # case 1-2. specific recommendation
                content = qa_instance.message_templates[
                    "specific_concept_recommendation_eng"
                ]
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
            "update_response_recommend_problem_eng completed",
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

    @tool(args_schema=DefaultChatToolArgs)
    def default_chat_tool() -> PromptToolMessageBundle:
        qa_instance.structured_logger.log_info(" 🛠️ default_chat executed")
        state.response_info.response_style.add(ResponseStyleMapEng.DEFAULT_CHAT)
        prompt_messages = qa_instance.call_manager.generate_prompt(
            "eduqa_eng/default_chat_eng",
            {
                "messages": state.messages,
                "problem_info": state.problem_info,
                "student_profile": qa_instance.student_profile,
                "grade": str(qa_instance.student_profile.grade),
            },
        )

        return concat_messages(prompt_messages)

    return [
        translation_tool,
        table_fetch_tool,
        answer_included_tool,
        recommend_problem_tool,
        default_chat_tool,
    ]
