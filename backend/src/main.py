# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import functools
import io
import os

from typing import Annotated

import yaml

from fastapi import Depends, FastAPI, Response
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

import all_models  # noqa: F401

from auths.presentation.http_exceptions import add_auths_exception_handlers
from chats.presentation.chat_router import router as chat_router
from chats.presentation.http_exceptions import add_chats_exception_handlers
from chats.presentation.problem_bookmark_router import router as problem_bookmark_router
from common.infra.swagger_auth import swagger_authenticate
from common.presentation.http_exceptions import app_exception_handlers
from config.config import cors_config, env_config, local_storage_config
from config.lifespan import app_lifespan
from config.middleware import DBMiddleware
from goals.presentation.http_exceptions import add_goal_exception_handlers
from goals.presentation.router import router as goal_router
from problems.presentation.http_exceptions import add_problems_exception_handlers
from problems.presentation.router import router as problem_router
from uploads.presentation.http_exceptions import add_uploads_exception_handlers
from uploads.presentation.router import router as upload_router
from users.presentation.http_exceptions import add_users_exception_handlers
from users.presentation.router import router as user_router

app = FastAPI(
    root_path="/api/v1",
    title="edu-max BE",
    version="0.0.1",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=app_lifespan,
    separate_input_output_schemas=False
)

origins = cors_config.CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(DBMiddleware)

app.include_router(chat_router, prefix="/chats", tags=["chats"])
app.include_router(problem_router, prefix="/problems", tags=["problems"])
app.include_router(upload_router, prefix="/uploads", tags=["upload"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(goal_router, prefix="/goals", tags=["goals"])
app.include_router(problem_bookmark_router, prefix="/problem-bookmarks", tags=["problem-bookmarks"])

app_exception_handlers(app)
add_chats_exception_handlers(app)
add_problems_exception_handlers(app)
add_uploads_exception_handlers(app)
add_users_exception_handlers(app)
add_goal_exception_handlers(app)
add_auths_exception_handlers(app)

# 로컬 환경이면, 로컬 스토리지 활용해서 서빙
if env_config.STORAGE == "LOCAL":
    os.makedirs(local_storage_config.UPLOAD_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory=local_storage_config.UPLOAD_DIR))


# 개발 서버나 스테이지 서버에서 긴급적으로 swagger 통해 쓸 일이 있을수도 있으므로, 암호화만 살림
_OPENAPI_JSON_PATH = f"{app.root_path}/openapi.json" if app.root_path else "/openapi.json"

@app.get("/redoc", include_in_schema=False)
def secured_dedoc(_ : Annotated[str, Depends(swagger_authenticate)]) -> HTMLResponse:
    return get_redoc_html(
        openapi_url=_OPENAPI_JSON_PATH,
        title="edu-max"
    )

@app.get("/docs", include_in_schema=False)
def secured_swagger_ui(_: Annotated[str, Depends(swagger_authenticate)]) -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=_OPENAPI_JSON_PATH,
        title="EDU-MAX - Swagger UI",
    )

@app.get("/openapi.json", include_in_schema=False)
def secured_openapi_json(_: Annotated[str, Depends(swagger_authenticate)]) -> JSONResponse:
    return JSONResponse(app.openapi())


@functools.lru_cache
def _openapi_yaml_cached() -> str:
    openapi_json = app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return yaml_s.getvalue()


@app.get("/openapi.yaml", include_in_schema=False)
def secured_openapi_yaml(_: Annotated[str, Depends(swagger_authenticate)]) -> Response:
    return Response(_openapi_yaml_cached(), media_type="text/yaml")


@app.get("/health")
async def health_check() -> Response:
    return Response("OK")
