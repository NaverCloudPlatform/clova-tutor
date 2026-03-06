# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langchain_core.tools import tool

from assistant.src.schema import ProblemHistory, ProblemInfo, State
from assistant.src.schema.common_tool_schema import (
    MakeProblemSummaryToolArgs,
    PersuasionToolArgs,
    ProblemInfoToolArgs,
)
from assistant.src.utils.call_utils import (
    get_equal_problem,
    get_grade_to_str,
    get_message,
    get_text_message,
    remove_equal_problem,
)
from assistant.src.utils.data_utils import get_objectives_for_grade
from assistant.src.utils.load_utils import load_model_param


def create_common_tools(qa_instance, state: State):

    _current_state = state

    @tool(args_schema=MakeProblemSummaryToolArgs)
    def make_problem_summary_tool() -> dict:
        state = _current_state if _current_state else state
        qa_instance.structured_logger.log_info("🛠️ make_problem_summary executed")
        last_ai_message = get_message(state, message_type=AIMessage, idx=-1)
        idx = -2 if last_ai_message.additional_kwargs.get("confirm_transition") else -1

        if state.problem_history:
            messages = state.messages[1:idx]
        else:
            messages = state.messages[:idx]

        summary = qa_instance.call_manager.invoke(
            "eduqa/make_problem_summary",
            {"messages": messages},
        )
        if summary and state.problem_info:
            problem_history = ProblemHistory(
                **state.problem_info.model_dump(), **summary
            )
            state.problem_history.append(problem_history)

            user_query_history = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "content": "과거 질문 내역:"
                        + ", ".join(
                            problem.question for problem in state.problem_history
                        ),
                    }
                ]
            )

            qa_instance.redis.save_problem_card(
                qa_instance.thread_config["configurable"]["thread_id"],
                problem_history,
                state.messages[:-1],
            )
            qa_instance.redis.clear_in_memory(
                qa_instance.thread_config["configurable"]["thread_id"]
            )
            qa_instance.redis.save_to_in_memory(
                qa_instance.thread_config["configurable"]["thread_id"],
                user_query_history,
            )
            state.messages.insert(0, user_query_history)
            state.messages = [RemoveMessage(id=m.id) for m in state.messages[1:-1]]

            qa_instance.structured_logger.log_node_end(
                "make_problem_summary",
                result_summary="Problem summary created successfully",
                additional_data={
                    "context": problem_history.context,
                    "keywords": problem_history.keywords,
                },
            )
            return {
                "messages": state.messages,
                "problem_history": state.problem_history,
            }

        qa_instance.structured_logger.log_node_end(
            "make_problem_summary",
            result_summary="No summary created",
        )
        return {"messages": state.messages, "problem_history": state.problem_history}

    @tool(args_schema=PersuasionToolArgs)
    def persuasion_tool() -> dict:
        state = _current_state if _current_state else state
        qa_instance.structured_logger.log_info("🛠️ persuasion_tool executed")

        ai_msg = AIMessage(
            content=[],
            additional_kwargs={
                "finalized_by_tool": "persuasion_tool",
                "prompt_name": "eduqa/update_persuasion",
            },
        )

        state.messages.append(ai_msg)
        return ai_msg

    @tool(args_schema=ProblemInfoToolArgs)
    def problem_info_tool() -> dict:
        state = _current_state if _current_state else state
        qa_instance.structured_logger.log_info("🛠️ problem_info_tool executed")

        subject_eng_name = "eng" if qa_instance.default_subject == "영어" else "math"
        qa_instance.structured_logger.log_node_start(
            f"update_problem_info",
            {
                "subject": subject_eng_name,
            },
        )

        from assistant.src.graphs.node.common_node import (
            get_problem_info_from_db,
            update_reference_problems,
        )

        update = {}
        source = ""  # Initialize source with default value
        if state.db_problem_id:
            # state changed: problem_info, subject_info, messages
            state = get_problem_info_from_db(qa_instance, state)
            reference_problems = update_reference_problems(qa_instance, state)
            update["reference_problems"] = reference_problems
            update["problem_info"] = state.problem_info
            update["subject_info"] = state.subject_info
            update["messages"] = state.messages
            source = "database fetch"
        else:
            # Skip update_reference_problems if topic is "추천" and reference_problems already exists
            # (it was already updated in update_subject_info)
            if state.subject_info and state.subject_info.topic:
                topics = (
                    state.subject_info.topic
                    if isinstance(state.subject_info.topic, list)
                    else [state.subject_info.topic]
                )
                if (
                    any("추천" in str(topic) for topic in topics)
                    and state.reference_problems
                ):
                    reference_problems = state.reference_problems
                    qa_instance.structured_logger.log_info(
                        "problem_info_tool: using existing reference_problems for recommendation",
                        {"section": state.subject_info.section},
                    )
                else:
                    reference_problems = update_reference_problems(qa_instance, state)
            else:
                reference_problems = update_reference_problems(qa_instance, state)

            if reference_problems:
                update["reference_problems"] = reference_problems
            elif state.reference_problems:
                # Keep existing reference_problems if update failed
                reference_problems = state.reference_problems
                update["reference_problems"] = reference_problems
            else:
                pass

            if reference_problems:
                threshold = 0.92 if qa_instance.default_subject == "영어" else 0.99
                equal_problem = get_equal_problem(
                    reference_problems, threshold=threshold
                )
                similar_problem = get_equal_problem(reference_problems, threshold=0.90)
            else:
                equal_problem = None
                similar_problem = None

            # return problem info from database if equal problem exists
            if equal_problem:
                update["problem_info"] = equal_problem
                remove_equal_problem(reference_problems, equal_problem)
                source = "database fetch"
            elif (
                state.subject_info
                and state.subject_info.topic
                and any("추천" in str(topic) for topic in topics)
            ):
                source = "skip: case of recommendation"
                pass
            else:
                # generate problem info
                problem_model_param = load_model_param("update_problem_info")
                user_query = get_text_message(state.messages[-1])

                response, usage = qa_instance.call_manager.invoke(
                    f"eduqa_{qa_instance.subject_eng_name}/update_problem_info_{qa_instance.subject_eng_name}",
                    {
                        "messages": state.messages,
                        "student_profile": qa_instance.student_profile,
                        "subject_info": state.subject_info,
                        "grade": get_grade_to_str(qa_instance.student_profile.grade),
                        "problem_in_query": user_query,
                        "similar_problem_info": similar_problem,
                        "learning_objectives": get_objectives_for_grade(
                            qa_instance.student_profile.grade
                        ),
                    },
                    model_param=problem_model_param,
                )

                if response:
                    response["question"] = user_query
                    problem_info = ProblemInfo(**response)
                    problem_info.subject_info = state.subject_info
                    update["problem_info"] = problem_info
                    source = "generated"
                else:
                    source = "generation_failed"

        qa_instance.structured_logger.log_node_end(
            f"update_problem_info",
            result_summary=f"Problem info {subject_eng_name} updated via source: {source}",
            additional_data={
                "source": source,
                "problem_info": update.get("problem_info", None),
            },
        )

        if update.get("problem_info") is not None:
            state.problem_info = update["problem_info"]
        if update.get("reference_problems") is not None:
            state.reference_problems = update["reference_problems"]
        return update

    tools = [
        make_problem_summary_tool,
        persuasion_tool,
        problem_info_tool,
    ]

    return tools
