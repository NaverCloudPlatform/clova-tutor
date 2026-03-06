# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import argparse
import asyncio
import os
import re
import subprocess
import sys
import uuid

import langchain

# mlflow server --host 0.0.0.0 --port 5000
import mlflow

langchain.debug = False  # Enable debug mode for LangChain

root_path = (
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
    .strip()
    .decode("utf-8")
)
sys.path.insert(1, os.path.join(root_path, "src"))


from assistant.src.graphs.draw import draw_graph
from assistant.src.models.eng import EduQAEng
from assistant.src.models.math import EduQAMath
from assistant.src.schema import ModelParam, State, StudentProfile
from assistant.src.utils.load_utils import load_yaml
from config.config import MlflowConfig, RedisClusterConfig
from config.redis_cluster import RedisManager, get_sync_redis_client

# Enabling tracing for LangGraph (LangChain)
mlflow.langchain.autolog()

# Set MLflow tracking URI and experiment from api_info.yaml
mlflow_config = MlflowConfig()
mlflow.set_experiment(mlflow_config.MLFLOW_EXPERIMENT_NAME)


api_info = load_yaml("assistant/api_info.yaml")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the simulation script.")
    parser.add_argument(
        "--loglevel",
        default="INFO",
        help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument(
        "--multiline",
        action="store_true",
        help="Enable multiline input mode (default: False)",
    )
    parser.add_argument(
        "--test_memory",
        action="store_true",
        help="Test memory system functionality (default: False)",
    )
    parser.add_argument(
        "--subject",
        choices=["eng", "math"],
        default="eng",
        help="Choose the subject domain: 'eng' or 'math' (default: eng)",
    )
    parser.add_argument(
        "--draw_graph",
        action="store_true",
        help="Draw and save the LangGraph structure, then exit",
    )
    parser.add_argument(
        "--db_problem_id",
        type=str,
        help="Optional DB problem ID to preload",
        default=None,
    )
    parser.add_argument(
        "--image_url",
        type=str,
        help="Optional image URL to include in the message",
        default=None,
    )
    parser.add_argument(
        "--grade",
        type=int,
        help="Optional grade level to assign to the agent",
        default=10,
    )
    parser.add_argument(
        "--block_advanced_learning",
        action="store_true",
        help="Block advanced learning",
    )
    parser.add_argument(
        "--no_block_advanced_learning",
        dest="block_advanced_learning",
        action="store_false",
        help="Do not block advanced learning",
    )
    parser.set_defaults(block_advanced_learning=False)

    check_draw_graph = parser.parse_args(["--draw_graph"])

    if check_draw_graph.draw_graph:
        extended_parser = argparse.ArgumentParser(parents=[parser], add_help=False)
        extended_parser.add_argument(
            "--hide_condition",
            action="store_true",
            default=False,
            help="Hide condition information in the graph",
        )
        extended_parser.add_argument(
            "--node_font_size",
            type=int,
            help="Set the font size of the nodes",
            default=10,
        )
        extended_parser.add_argument(
            "--edge_font_size",
            type=int,
            help="Set the font size of the edges",
            default=10,
        )
        extended_parser.add_argument(
            "--uniform_color",
            action="store_true",
            default=False,
            help="Use uniform color for all nodes",
        )
        args = extended_parser.parse_args()
    else:
        args = parser.parse_args()
    return args


def create_qa_instance(
    subject: str,
    student_profile: StudentProfile,
    model_param: ModelParam,
    block_advanced_learning: bool,
    loglevel: str,
    redis_client=None,
):
    if subject == "math":
        return EduQAMath(
            student_profile=student_profile,
            loglevel=loglevel,
            model_param=model_param,
            redis_client=redis_client,
            block_advanced_learning=block_advanced_learning,
        )
    else:
        return EduQAEng(
            student_profile=student_profile,
            loglevel=loglevel,
            model_param=model_param,
            redis_client=redis_client,
        )


def get_info_from_query(user_query: str):
    # get additional info from user query
    info = {
        "db_problem_id": None,
    }  # TODO: image_url

    match = re.match(r"^\s*\[([\w\d\.\/:]+)]\s*(.*)", user_query)
    if match:
        add_info = match.group(1)
        user_query = match.group(2)

        if add_info.startswith("http"):
            info["image_url"] = add_info
        elif add_info.isdigit():
            info["db_problem_id"] = add_info
        else:
            raise ValueError(
                f"Invalid additional info format: {add_info}. "
                "Expected format: [<image_url>], or [<db_problem_id>]."
            )
    return user_query.strip(), info


def get_user_query(args, state):
    # get user input
    if args.multiline:
        print("Human (ctrl+d 입력 시 종료): ", end="", flush=True)
        user_query = sys.stdin.read()
    else:
        print("Human: ", end="", flush=True)
        user_query = sys.stdin.readline()

    user_query, add_info = get_info_from_query(user_query)

    for key, value in add_info.items():
        if getattr(state, key, None) != value and value is not None:
            setattr(state, key, value)

    return state, user_query


async def main():
    args = parse_arguments()

    student_profile = StudentProfile(
        user_id="f97ba8d5-642e-4648-97e7-1df06ff382ee", name="조혜정", grade=args.grade
    )

    model_param = ModelParam(model="hcx-005", temperature=0.5)

    # Initialize Redis Cluster Manager with new API
    redis_config = RedisClusterConfig(
        RC_SEED_URL=api_info["redis-cluster"]["seed_url"],
        RC_PASSWORD=api_info["redis-cluster"]["password"],
    )
    redis_manager = await RedisManager.ensure_initialized(redis_config)
    redis_client = get_sync_redis_client()

    edu_qa = create_qa_instance(
        subject=args.subject,
        student_profile=student_profile,
        model_param=model_param,
        block_advanced_learning=args.block_advanced_learning,
        loglevel=args.loglevel.upper(),
        redis_client=redis_client,
    )

    if args.draw_graph:
        output_path = f"langgraph_{args.subject}"
        draw_graph(
            edu_qa.graph,
            output_path,
            hide_condition=args.hide_condition,
            node_font_size=args.node_font_size,
            edge_font_size=args.edge_font_size,
            uniform_color=args.uniform_color,
        )
        return

    state = State(
        db_problem_id=args.db_problem_id,
        messages=[],
    )

    # image: https://kr.object.ncloudstorage.com/edu-bucket/chat-upload/e189dc83-c219-44be-a82e-e1486e8c90c8.png
    # image: https://www.mathfactory.net/wp-content/uploads/%EC%88%98%ED%95%99-%EA%B3%B5%EC%8B%9D-%EC%9D%B4%EC%B0%A8%ED%95%A8%EC%88%98-%EC%A7%81%EC%84%A0-01.png
    is_first_turn = True
    while True:
        state, user_query = get_user_query(args, state)

        # finalize session
        if user_query.strip(" \n") == "end":
            break

        message_content = [{"type": "text", "content": user_query.strip()}]

        if is_first_turn:
            if args.image_url:
                message_content.append({"type": "image", "content": args.image_url})
            is_first_turn = False

        state.messages.append(
            {
                "role": "user",
                "content": message_content,
            }
        )

        first = True
        if mlflow.active_run() is not None:
            mlflow.end_run()

        with mlflow.start_run(run_name=f"{uuid.uuid4().hex}", nested=False) as run:
            async for state_chunk in edu_qa.astream(state, model_param):
                if first:
                    print("Assistant: ", end="", flush=True)
                    first = False
                print(state_chunk.model_response, end="", flush=True)
        print("")
        state = State(**edu_qa.graph.get_state(edu_qa.thread_config).values)
        # mimic BE operation
        state.db_problem_id = None
        # print(state.model_dump_json(indent=2))

    if args.test_memory:
        edu_qa.save_long_term_memory()

    # redis clear (for sim)
    edu_qa.redis.delete_all_for_user(edu_qa.thread_config["configurable"]["thread_id"])
    await redis_manager.close()
    # unknown db clear
    edu_qa.unknown_concept_db.delete_unknown_concepts()


if __name__ == "__main__":
    asyncio.run(main())
