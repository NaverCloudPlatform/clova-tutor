# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import mlflow

from config.grpc import serve_grpc
from config.redis_cluster import RedisManager, init_redis
from config.config import mlflow_config, env_config, redis_cluster_config


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    redis_cluster_manager: RedisManager | None = None
    try:
        redis_cluster_manager = await init_redis(redis_cluster_config)
        asyncio.create_task(serve_grpc())

        # MLFLOW Experiment 세팅을 설정합니다.
        # edu-agent-dev 이런 식으로 설정함
        mlflow.set_experiment(
            f"{mlflow_config.MLFLOW_EXPERIMENT_NAME}-{env_config.ENV}"
        )
        yield

    finally:
        if redis_cluster_manager is not None:
            await redis_cluster_manager.close()
        mlflow.end_run()
