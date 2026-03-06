# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import grpc

from assistant_adapter.dependencies import get_assistant_handler
from config.config import service_config
from grpc_stubs import modelchat_pb2_grpc


async def serve_grpc():
    handler = get_assistant_handler()

    server = grpc.aio.server()
    modelchat_pb2_grpc.add_ModelServiceServicer_to_server(handler, server)

    server.add_insecure_port(f"[::]:{service_config.GRPC_PORT}")
    await server.start()
    await server.wait_for_termination()
