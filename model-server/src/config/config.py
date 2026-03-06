# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Literal

from pydantic_settings import BaseSettings


class ServiceConfig(BaseSettings):
    RESPONSE_MODEL: str = ""
    GRPC_PORT: int = 0


class RedisClusterConfig(BaseSettings):
    RC_SEED_URL: str = ""
    RC_PASSWORD: str = ""


class ModelConfig(BaseSettings):
    DEFAULT_PROMPT_PATH: str = "assistant/prompt"
    ANSWER_TEMPLATE_PATH: str = "assistant/answer_template"
    CONTENT_TEMPLATE_PATH: str = "assistant/content_template"
    DATA_PATH: str = "assistant/data"
    MODEL_OPTION: str = "assistant/src/options"
    HSO_PROMPT_PATH: str = "assistant/src/hcx_structured_output/src/prompt"


class EnvConfig(BaseSettings):
    ENV: Literal["LOCAL", "DEV", "PROD", "TEST"] = "LOCAL"


class WeaviateConfig(BaseSettings):
    PROBLEM_INDEX: str = "Problem_opensource"
    CURRICULUM_INDEX: str = "Curriculum_opensource"


class MlflowConfig(BaseSettings):
    MLFLOW_EXPERIMENT_NAME: str = "edu-agent"
    MLFLOW_TRACKING_URL: str = ""


class CORSConfig(BaseSettings):
    CORS_ORIGINS: str = ""


service_config = ServiceConfig()
redis_cluster_config = RedisClusterConfig()
model_config = ModelConfig()
env_config = EnvConfig()
mlflow_config = MlflowConfig()
weaviate_config = WeaviateConfig()
cors_config = CORSConfig()
