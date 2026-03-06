# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Literal

from pydantic_settings import BaseSettings


class ServiceConfig(BaseSettings):
    RESPONSE_MODEL: str = ""
    MODEL_SERVER_GRPC_URL: str = ""


class DBConfig(BaseSettings):
    MYSQL_HOST: str = ""
    MYSQL_PORT: str = ""
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = ""


class ObjectStorageConfig(BaseSettings):
    OS_SERVICE_NAME: str = ""
    OS_ENDPOINT_URL: str = ""
    OS_REGION_NAME: str = ""
    OS_ACCESS_KEY: str = ""
    OS_SECRET_KEY: str = ""
    OS_BUCKET_NAME: str = ""


class EnvConfig(BaseSettings):
    ENV: Literal["LOCAL", "DEV", "PROD","TEST"] = "LOCAL"
    STORAGE: Literal["LOCAL","NCP"] = "LOCAL"

class SwaggerConfig(BaseSettings):
    SWAGGER_USERNAME: str = ""
    SWAGGER_PASSWORD: str = ""

class RedisClusterConfig(BaseSettings):
    RC_SEED_URL: str = ""
    RC_PASSWORD: str = ""
    RC_TTL: int = 60

class InternalApiKey(BaseSettings):
    INTERNAL_API_KEY: str = ""


class LocalStorageConfig(BaseSettings):
    UPLOAD_DIR: str = "static"
    SECRET_KEY: str = ""
    URL_EXPIRY_SECONDS: int = 60
    BASE_URL: str = "http://localhost:8000/api/v1"

class CORSConfig(BaseSettings):
    CORS_ORIGINS: str = ""


service_config = ServiceConfig()
db_config = DBConfig()
redis_clutser_config = RedisClusterConfig()
object_storage_config = ObjectStorageConfig()
env_config = EnvConfig()
swagger_config = SwaggerConfig()
internal_api_key = InternalApiKey()
local_storage_config = LocalStorageConfig()
cors_config = CORSConfig()
