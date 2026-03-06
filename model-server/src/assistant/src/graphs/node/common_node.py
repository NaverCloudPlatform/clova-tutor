# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, Literal

from assistant.src.graphs.tools.common_tools import create_common_tools
from assistant.src.graphs.tools.math_tools import create_pre_math_tools
from assistant.src.schema import ResponseInfo, State, SubjectInfo
from assistant.src.utils.call_utils import (
    convert_message_content,
    convert_to_problem_info,
    convert_to_reference_problems,
    get_grade_to_str,
    get_problem_group_by_level,
    get_text_message,
    retry_on_parse_error,
)
from assistant.src.utils.data_utils import (
    get_grammar_topic,
    get_sections_for_grade_range,
    section2grade,
)
from assistant.src.utils.load_utils import load_additional_model_param
from config.config import weaviate_config


def default_chat(qa_instance, state: State) -> Command[Literal["finalize_chat"]]:
    if state.messages:
        last = state.messages[-1]
        if (
            isinstance(last, AIMessage)
            and last.additional_kwargs.get("finalized_by_tool") == "persuasion_tool"
        ):
            prompt_name = last.additional_kwargs.get(
                "prompt_name", "eduqa/update_persuasion"
            )
            prompt_args = {
                "messages": state.messages,
                "subject_info": state.subject_info,
            }

            response = qa_instance.call_manager.invoke(prompt_name, prompt_args)
            return Command(
                update={
                    "messages": [
                        AIMessage(
                            content=[{"type": "text", "content": response.content}],
                            additional_kwargs={
                                "type": "end",
                                "usage": response.usage_metadata,
                            },
                        )
                    ]
                },
                goto="finalize_chat",
            )

    # Simple node - log_info only
    current_subject = (
        state.subject_info.subject
        if state.subject_info and state.subject_info.subject
        else None
    )

    qa_instance.structured_logger.log_info(
        "default_chat executed",
        {
            "subject": current_subject,
            "problem_info": state.problem_info,
            "student_profile": qa_instance.student_profile,
        },
    )

    if qa_instance.default_subject == current_subject:
        prompt_name = f"eduqa_{qa_instance.subject_eng_name}/default_chat_{qa_instance.subject_eng_name}"
    else:
        prompt_name = f"eduqa_{qa_instance.subject_eng_name}/default_chat_others"

    args = {
        "messages": state.messages,
        "problem_info": state.problem_info,
        "student_profile": qa_instance.student_profile,
        "grade": str(qa_instance.student_profile.grade),
    }

    if state.level_instruction:
        args.update(level_instruction=qa_instance.student_profile.grade)

    response = qa_instance.call_manager.invoke(
        prompt_name,
        args,
    )
    return Command(
        update={
            "messages": [
                AIMessage(
                    content=[{"type": "text", "content": response.content}],
                    additional_kwargs={
                        "type": "end",
                        "usage": response.usage_metadata,
                    },
                )
            ]
        },
        goto="finalize_chat",
    )


def finalize_chat(qa_instance, state: State):
    # remove messages when if the last message is a reject_advanced_learning
    # Error/Edge case - log_node_start + appropriate level
    if (
        qa_instance.message_templates["reject_advanced_learning"].strip("\n")
        in state.messages[-1].content
    ):
        state.messages = [RemoveMessage(id=m.id) for m in state.messages[-2:]]

    usage = (
        getattr(state.messages[-1], "additional_kwargs", {}).get("usage", {})
        if state.messages
        else {}
    )

    if usage.get("total_tokens", 0) > 5_000:
        qa_instance.structured_logger.log_node_start(
            "finalize_chat",
            {
                "reason": "token_limit_exceeded (over 5000)",
                "total_tokens": usage.get("total_tokens", 0),
                "message": "Summary Start",
            },
        )
        # state.problem_history가 있다면 state.messages[1]은 과거 대화 questions
        msgs_to_summarize = (
            state.messages[1:] if state.problem_history else state.messages
        )
        summary = qa_instance.call_manager.invoke(
            "eduqa/make_problem_summary", {"messages": msgs_to_summarize}
        )
        if summary:
            remove_msgs = [RemoveMessage(id=m.id) for m in msgs_to_summarize]
            new_messages = [
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "content": f"과거 대화 요약: {summary['context']}",
                        }
                    ]
                )
            ]

            qa_instance.redis.clear_in_memory(
                qa_instance.thread_config["configurable"]["thread_id"]
            )
            if state.problem_history:
                qa_instance.redis.save_to_in_memory(
                    qa_instance.thread_config["configurable"]["thread_id"],
                    state.messages[0],
                )
            qa_instance.redis.save_to_in_memory(
                qa_instance.thread_config["configurable"]["thread_id"], new_messages[0]
            )
            state.messages = remove_msgs + new_messages

        qa_instance.structured_logger.log_node_end(
            "finalize_chat",
            result_summary="Token limit summary completed",
            additional_data={"summary_length": len(str(summary)) if summary else 0},
        )

    return state


def get_problem_info_from_db(
    qa_instance, state: State
) -> Command[Literal["pre_model_pipeline"]]:
    # check whether the db_problem_info is None
    # Core node - log_node_start + log_node_end + detailed logging

    # check if the problem info is already in the state
    if state.problem_info:
        if state.problem_info.problem_id == state.db_problem_id:
            qa_instance.structured_logger.log_debug(
                "get_problem_info_from_db: already in state",
                {"problem_id": state.db_problem_id},
            )
            return Command(update=state, goto="pre_model_pipeline")

    qa_instance.structured_logger.log_node_start(
        "get_problem_info_from_db",
        {
            "db_problem_id": state.db_problem_id,
            "function": "get_problem_info_from_db",
        },
    )

    index = weaviate_config.PROBLEM_INDEX
    retrieved_problem = qa_instance.retrieve(
        index,
        "query",  # dummy query to retrieve the problem
        k=1,
        data_filter={"problem_id": state.db_problem_id},
    )

    if not retrieved_problem:
        qa_instance.structured_logger.log_warning(
            "get_problem_info_from_db: no problem found",
            {
                "db_problem_id": state.db_problem_id,
                "index": index,
                "function": "get_problem_info_from_db",
            },
        )
        return Command(update=state, goto="pre_model_pipeline")

    # update problem info
    problem_info = convert_to_problem_info(
        qa_instance.default_subject, retrieved_problem[0][0]["metadata"]
    )

    subject_info = state.subject_info
    if subject_info is None:
        subject_info = SubjectInfo(
            subject=qa_instance.default_subject,
            section=problem_info.subject_info.section,
            topic=problem_info.subject_info.topic,
        )
    else:
        if qa_instance.default_subject == "수학":
            subject_info.section = problem_info.subject_info.section
        subject_info.unit = problem_info.subject_info.unit

    qa_instance.structured_logger.log_node_end(
        "get_problem_info_from_db",
        result_summary="Problem info retrieved successfully",
        additional_data={
            "problem_info": state.problem_info,
            "subject_info": state.subject_info,
        },
    )

    # add image_url to user_query
    messages = state.messages
    if problem_info.has_image:
        messages[-1].content.append(
            {"type": "image", "content": problem_info.image_url}
        )

    state.problem_info = problem_info
    state.subject_info = subject_info
    state.messages = messages
    state.reference_problems = update_reference_problems(qa_instance, state)

    return Command(update=state, goto="pre_model_pipeline")


def initialize_state(
    qa_instance, state: State
) -> Command[Literal["update_subject_info", "get_problem_info_from_db"]]:
    """
    next: update_subject_info
    db_problem_id: get_problem_info_from_db
    """
    # Medium node - log_node_start + log_info
    qa_instance.structured_logger.log_node_start("initialize_state")

    default_state = State(
        student_profile=qa_instance.student_profile,
        default_subject=qa_instance.default_subject,
        db_problem_id=state.db_problem_id,  # BE input
        messages=[],
    )
    if qa_instance.default_subject == "수학":
        qa_instance.block_advanced_learning = qa_instance.block_advanced_learning

    # need to maintain
    maintain_fields = [
        "messages",
        "subject_info",
        "problem_info",
        "problem_history",
        "reference_problems",
        "response_info",
        "recommended_problem_ids",  # Preserve recommendation history across turns
    ]
    for field in maintain_fields:
        setattr(default_state, field, getattr(state, field))

    qa_instance.structured_logger.log_info(
        "initialize_state completed",
        {
            "subject": qa_instance.default_subject,
        },
    )
    if state.db_problem_id:
        return Command(
            update=default_state.model_dump(exclude_none=False),
            goto="get_problem_info_from_db",
        )
    else:
        return Command(
            update=default_state.model_dump(exclude_none=False),
            goto="update_subject_info",
        )


def reject_advanced_learning(
    qa_instance, state: State
) -> Command[Literal["finalize_chat"]]:
    # Error/Edge case - log_node_start only
    qa_instance.structured_logger.log_node_start("reject_advanced_learning")
    return Command(
        update={
            "messages": [
                AIMessage(
                    content=[
                        {
                            "type": "text",
                            "content": qa_instance.message_templates[
                                "reject_advanced_learning"
                            ],
                        }
                    ],
                    additional_kwargs={
                        "type": "end",
                    },
                )
            ]
        },
        goto="finalize_chat",
    )


def say_cannot_understand(qa_instance, state: State):
    # Error/Edge case - log_node_start only
    qa_instance.structured_logger.log_node_start("say_cannot_understand")
    return {
        "messages": [
            AIMessage(
                content=[
                    {
                        "type": "text",
                        "content": qa_instance.message_templates[
                            "say_cannot_understand"
                        ],
                    }
                ],
            )
        ]
    }


def start_chat(qa_instance, state: State) -> Command[Literal["initialize_state"]]:
    """
    default: initialize_state
    """
    return Command(goto="initialize_state")


@retry_on_parse_error
def update_subject_info(qa_instance, state: State) -> Command[
    Literal[
        "pre_model_pipeline",
        "reject_listening",
        "reject_advanced_learning",
        "default_chat",
    ]
]:
    """
    reject: reject_listening
    reject_advanced_learning: reject_advanced_learning
    default, parsing_error: default_chat
    next: pre_model_pipeline
    """
    subject_info = None

    qa_instance.structured_logger.log_node_start(
        "update_subject_info",
        {
            "subject": qa_instance.subject_eng_name,
        },
    )

    # 새로운 문제를 입력했을 때, 기존 문제 정보를 사용하지 않고 새로운 문제 정보를 사용 (get_problem_info_from_db에서 추출된 정보)
    # db_problem_id가 있을 때만 LLM 호출을 스킵 (멀티턴에서는 LLM 호출 필요)
    if state.db_problem_id:
        return Command(
            update={"subject_info": state.subject_info}, goto="pre_model_pipeline"
        )

    min_temp_param = load_additional_model_param("minimum_temperature")
    response, usage = qa_instance.call_manager.invoke(
        f"eduqa_{qa_instance.subject_eng_name}/update_subject_info_{qa_instance.subject_eng_name}",
        {
            "messages": state.messages,
            "student_profile": qa_instance.student_profile,
            "question": (state.problem_info.question if state.problem_info else "None"),
            "grammar_topic": get_grammar_topic(),
            "section_category": get_sections_for_grade_range(
                qa_instance.student_profile.grade
            ),
            "grade": get_grade_to_str(qa_instance.student_profile.grade),
        },
        additional_params=min_temp_param,
    )

    if qa_instance.default_subject == "수학":
        if (
            response
            and response.get("section") != "기타"
            and response.get("subject") != "기타"
        ):
            # unit과 topic이 없을 수 있음
            section = response.get("section", "")
            unit = response.get("unit", "")
            topic = response.get("topic", "")
            if isinstance(topic, list):
                topic = ", ".join(topic) if topic else ""
            elif not isinstance(topic, str):
                topic = str(topic) if topic else ""

            standard_curriculum = qa_instance.retrieve(
                weaviate_config.CURRICULUM_INDEX,
                f"대단원:{section}\n중단원:{unit}\n주제:{topic}",
                k=1,
                data_filter={
                    "grade": str(qa_instance.student_profile.grade),
                },
            )

            if standard_curriculum:
                qa_instance.structured_logger.log_debug(
                    f"update_subject_info_{qa_instance.subject_eng_name}: curriculum score",
                    {"score": standard_curriculum[0][1]},
                )
                if standard_curriculum[0][1] >= 0.9:
                    candidates = standard_curriculum[0][0]
                    response["section"] = candidates["metadata"]["section"]
                    response["unit"] = candidates["metadata"]["unit"]
                    response["topic"] = [candidates["metadata"]["topic"]]

    if response:
        # retrieve accurate section
        subject_info = SubjectInfo(**response)
        qa_instance.structured_logger.log_node_end(
            "update_subject_info",
            result_summary="Subject info updated successfully",
            additional_data={
                "subject": qa_instance.subject_eng_name,
                "response": response,
            },
        )

    update = {
        "subject_info": subject_info,
        "recommended_problem_ids": state.recommended_problem_ids
        or [],  # Preserve recommendation history
    }

    # If topic is "추천", update reference_problems from DB
    # This ensures reference_problems are available for recommend_problem_tool
    # Note: pre_model_pipeline will skip problem_info_tool if reference_problems already exists
    if subject_info and subject_info.topic:
        topics = (
            subject_info.topic
            if isinstance(subject_info.topic, list)
            else [subject_info.topic]
        )
        if any("추천" in str(topic) for topic in topics):
            # Update state with subject_info for reference_problems retrieval
            state.subject_info = subject_info
            reference_problems = update_reference_problems(qa_instance, state)
            if reference_problems:
                update["reference_problems"] = reference_problems
                qa_instance.structured_logger.log_info(
                    "update_subject_info: reference_problems updated for recommendation",
                    {
                        "section": subject_info.section,
                        "subject": qa_instance.subject_eng_name,
                        "has_reference_problems": True,
                    },
                )
            else:
                qa_instance.structured_logger.log_info(
                    "update_subject_info: no reference_problems found for recommendation",
                    {
                        "section": subject_info.section,
                        "subject": qa_instance.subject_eng_name,
                        "has_reference_problems": False,
                    },
                )

    # determine the next node
    # 1. check whether it is advanced learning
    if qa_instance.default_subject == "수학" and subject_info:
        is_other_section = subject_info.section == "기타"
        is_advanced = False
        if subject_info.section and not is_other_section:
            section_grade = (
                section2grade(subject_info.section, subject_info.unit)
                if qa_instance.student_profile.grade < 10
                else section2grade(subject_info.section)
            )
            is_advanced = section_grade > qa_instance.student_profile.grade

        block_advanced_learning = getattr(qa_instance, "block_advanced_learning", True)
        if block_advanced_learning:
            # block_advanced_learning = True: 선행학습 방지 적용
            # section이 "기타"이거나 선행학습인 경우 reject_advanced_learning으로 바로 이동
            if is_other_section or is_advanced:
                qa_instance.structured_logger.log_info(
                    "update_subject_info: blocking advanced learning",
                    {
                        "is_other_section": is_other_section,
                        "is_advanced": is_advanced,
                        "block_advanced_learning": block_advanced_learning,
                        "section": subject_info.section if subject_info else None,
                    },
                )
                return Command(update=update, goto="reject_advanced_learning")
        else:
            # block_advanced_learning = False: 선행학습 허용, default_chat에서 처리
            if is_other_section or is_advanced:
                update.update(level_instruction=True)
                return Command(update=update, goto="default_chat")

    # 2. check whether it is listening
    if (
        qa_instance.default_subject == "영어"
        and subject_info
        and subject_info.section == "듣기"
    ):
        return Command(update=update, goto="reject_listening")

    # 3. check whether subject_info is invalid
    if subject_info and subject_info.section is None:
        return Command(update=update, goto="default_chat")

    # 4. Use pre-model-pipeline
    state.subject_info = subject_info
    return Command(update=update, goto="pre_model_pipeline")


def update_reference_problems(qa_instance, state: State):
    # Core node - log_node_start + log_node_end + detailed logging
    qa_instance.structured_logger.log_node_start(
        "update_reference_problems",
        {
            "subject": qa_instance.subject_eng_name,
        },
    )

    user_query = get_text_message(state.messages[-1])
    # add section to user query if subject is eng
    if qa_instance.default_subject == "영어":
        user_query = (
            "대단원:"
            + state.subject_info.section
            + "\n중단원:"
            + state.subject_info.unit
            + "\n문항:"
            + user_query
        )
        # set filter
        data_filter = {
            "grade": qa_instance.student_profile.grade,
            "subject": qa_instance.default_subject,
        }
    else:
        user_query = "중단원:" + state.subject_info.unit + "\n문항:" + user_query
        data_filter = {
            "grade": qa_instance.student_profile.grade,
            "subject": qa_instance.default_subject,
            "section": state.subject_info.section,
        }

    # retrieve problems according to level
    retrieved_problems = []
    for i in range(3):
        retrieved_problem = qa_instance.retrieve(
            weaviate_config.PROBLEM_INDEX,
            user_query,
            k=4,
            data_filter={**data_filter, "level": f"{i+1}"},
        )
        if retrieved_problem:
            retrieved_problems += retrieved_problem

    reference_problems = None
    if retrieved_problems:
        # remove the problem that user already solved
        if state.db_problem_id:
            retrieved_problems = [
                problem
                for problem in retrieved_problems
                if problem[0]["metadata"]["problem_id"] != state.db_problem_id
            ]

        # convert to recommended problem
        reference_problems_info = convert_to_reference_problems(
            qa_instance.default_subject, retrieved_problems
        )
        reference_problems = get_problem_group_by_level(reference_problems_info)
        ids_by_level = (
            {
                level: [
                    p.problem_info.problem_id
                    for p in getattr(reference_problems, level)
                ]
                for level in ("easy", "normal", "hard")
            }
            if reference_problems
            else None
        )

        qa_instance.structured_logger.log_node_end(
            "update_reference_problems",
            result_summary="Reference problems updated successfully",
            additional_data={
                "subject": qa_instance.subject_eng_name,
                "ids_by_level": ids_by_level,
            },
        )
    return reference_problems


def update_recommend_problem(qa_instance, state: State):
    # TODO: remove student already solved
    # Simple node - log_info only
    level_map = {1: "easy", 2: "normal", 3: "hard"}

    reference_problems = state.reference_problems
    problem_info = state.problem_info

    response_info = getattr(state, "response_info", None) or ResponseInfo()
    response_style = getattr(response_info, "response_style", None)
    more_difficult = getattr(response_info, "more_difficult", None)
    previous_recommend_id = getattr(response_info, "recommend_problem", None)

    # Get all previously recommended problem IDs in this session
    recommended_history = state.recommended_problem_ids or []

    # Check if user has actually solved any problems
    has_solved_problems = bool(state.problem_history and len(state.problem_history) > 0)

    if reference_problems:
        candidates = reference_problems.normal  # 기본값: normal 레벨

        # Case 1: user is solving a problem and wants harder one
        if problem_info:
            is_difficult = (
                more_difficult
                and problem_info.level
                and problem_info.level != 1
                and response_style == qa_instance.response_style_map.RECOMMEND_PROBLEM
            )
            if is_difficult:
                candidates = reference_problems.hard

        # Case 2: user was recommended a problem and wants harder one
        elif more_difficult and previous_recommend_id:
            # Find the previous recommended problem's level
            all_problems = (
                reference_problems.easy
                + reference_problems.normal
                + reference_problems.hard
            )
            previous_problem = next(
                (
                    p
                    for p in all_problems
                    if p.problem_info.problem_id == previous_recommend_id
                ),
                None,
            )

            if previous_problem:
                prev_level = previous_problem.problem_info.level
                # Select one level higher
                if prev_level == 1:  # easy -> normal
                    candidates = reference_problems.normal
                elif prev_level == 2:  # normal -> hard
                    candidates = reference_problems.hard
                else:  # hard -> stay at hard
                    candidates = reference_problems.hard

        # Filter out the problem user is currently solving
        if problem_info:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.problem_info.problem_id != problem_info.problem_id
            ]

        # Filter out all previously recommended problems in this session
        if recommended_history:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.problem_info.problem_id not in recommended_history
            ]

        # If no candidates left after filtering, try all levels
        if not candidates:
            all_problems = (
                reference_problems.easy
                + reference_problems.normal
                + reference_problems.hard
            )
            # Filter out previously recommended and currently solving problems
            candidates = [
                p
                for p in all_problems
                if p.problem_info.problem_id not in recommended_history
                and (
                    not problem_info
                    or p.problem_info.problem_id != problem_info.problem_id
                )
            ]

        if candidates:
            best_candidate = max(candidates, key=lambda x: x.similarity_score)
            response_info.recommend_problem = best_candidate.problem_info.problem_id
            raw_level = getattr(best_candidate.problem_info, "level", None)
            level = level_map.get(raw_level, "none")
            response_info.no_problems_reason = None

            # Add to recommended history
            if response_info.recommend_problem not in recommended_history:
                recommended_history.append(response_info.recommend_problem)
                state.recommended_problem_ids = recommended_history
        else:
            response_info.recommend_problem = ""
            level = "none"
            # Distinguish between "solved all" vs "no more recommendations without solving"
            if has_solved_problems:
                response_info.no_problems_reason = "all_solved"
            else:
                response_info.no_problems_reason = "all_recommended"
    else:
        response_info.recommend_problem = ""
        level = "none"
        response_info.no_problems_reason = "no_data"

    qa_instance.structured_logger.log_info(
        "update_recommend_problem completed",
        {
            "recommend_problem": response_info.recommend_problem,
            "level": level,
            "recommended_history_count": len(recommended_history),
        },
    )

    return response_info


def pre_model_pipeline(
    qa_instance, state: State
) -> Command[Literal["response_react_agent", "default_chat"]]:
    qa_instance.structured_logger.log_node_start("pre-model-pipeline")

    # Reset HSO token counter at function start
    qa_instance.call_manager.tool_llm.reset_hso_token_usage()

    common_tools = create_common_tools(qa_instance, state)
    include = set()
    if not (state.db_problem_id and state.problem_info and state.reference_problems):
        include.add("problem_info_tool")

    if len(state.messages) >= 2:
        include.update({"persuasion_tool", "make_problem_summary_tool"})

    if include:
        tools = [t for t in common_tools if getattr(t, "name", None) in include]
        if qa_instance.default_subject == "수학" and len(state.messages) >= 2:
            detect_unknown_concept_math_tool = create_pre_math_tools(
                qa_instance, state
            )[0]
            if detect_unknown_concept_math_tool.name not in {t.name for t in tools}:
                tools.append(detect_unknown_concept_math_tool)

        routed_messages = convert_message_content(state.messages)
        # Clear tool_prompt_path to ensure pre_model_pipeline always uses generic prompt_tool_call.yaml
        # (subject-specific prompts are only used in response_react_agent)
        tool_llm = qa_instance.call_manager.tool_llm
        if hasattr(tool_llm, "__dict__") and "tool_prompt_path" in tool_llm.__dict__:
            del tool_llm.__dict__["tool_prompt_path"]
        tool_bound = tool_llm.bind_tools(
            tools, tool_choice="auto", max_retries=5, tool_select_recursion=True
        )

        # tool selection
        ai_with_calls = tool_bound.invoke(routed_messages)
        tool_calls = ai_with_calls.tool_calls or []
        seen = set()
        tool_calls = [
            tc for tc in tool_calls if not (tc["name"] in seen or seen.add(tc["name"]))
        ]

        # Get HSO token usage for this function
        hso_usage = qa_instance.call_manager.tool_llm.get_hso_token_usage()

        if not tool_calls:
            qa_instance.structured_logger.log_node_end(
                "pre_model_pipeline",
                result_summary="No tool selected, proceeding to response_react_agent",
                additional_data={"hso_token_usage": hso_usage},
            )
            return Command(update=state, goto="response_react_agent")

        # tool execution
        ai_with_calls.tool_calls = tool_calls
        ai_with_calls.additional_kwargs["tool_calls"] = [
            {
                "id": tc["id"],
                "type": "function",
                "function": {"name": tc["name"], "arguments": tc.get("args", {})},
            }
            for tc in tool_calls
        ]
        selected_names = {tc["name"] for tc in tool_calls}
        tools_for_exec = [
            t for t in tools if getattr(t, "name", None) in selected_names
        ]
        tool_node = ToolNode(tools_for_exec)
        _ = tool_node.invoke([*routed_messages, ai_with_calls])
        if any(getattr(t, "name", None) == "persuasion_tool" for t in tools_for_exec):
            qa_instance.structured_logger.log_node_end(
                "pre_model_pipeline",
                result_summary="persuasion_tool executed, proceeding to default_chat",
                additional_data={"hso_token_usage": hso_usage},
            )
            return Command(update=state, goto="default_chat")

        qa_instance.structured_logger.log_node_end(
            "pre_model_pipeline",
            result_summary="tools executed, proceeding to response_react_agent",
            additional_data={"hso_token_usage": hso_usage},
        )
    return Command(update=state, goto="response_react_agent")
