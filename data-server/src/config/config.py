# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    WEAVIATE_HOST: str = "localhost"
    WEAVIATE_PORT: int = 8080


class CORSConfig(BaseSettings):
    CORS_ORIGINS: str = ""


class ClovaStudioConfig(BaseSettings):
    CLOVA_STUDIO_URL: str = ""
    CLOVA_STUDIO_HOST: str = ""
    CLOVA_STUDIO_API_KEY: str = ""
    CLOVA_STUDIO_GW_API_KEY: str = ""
    CLOVA_STUDIO_REQUEST_ID: str = ""
    CLOVA_STUDIO_APP_ID: str = ""

class FireworksConfig(BaseSettings):
    FIREWORKS_HOST: str = ""
    FIREWORKS_URL: str = "/inference/v1/embeddings"
    FIREWORKS_CLIENT_ID: str = ""
    FIREWORKS_CLIENT_SECRET: str = ""
    FIREWORKS_APP_ID: str = ""
    FIREWORKS_ACCESS_TOKEN: str = ""


class HuggingFaceConfig(BaseSettings):
    HUGGINGFACE_EMBEDDING_KEY: str = ""


load_dotenv(find_dotenv())

db_config = DBConfig()
huggingface_config = HuggingFaceConfig()
clovastudio_config = ClovaStudioConfig()
fireworks_config = FireworksConfig()
cors_config = CORSConfig()
