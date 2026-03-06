# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import FastAPI, Response
from starlette.middleware.cors import CORSMiddleware

from config.lifespan import app_lifespan
from config.config import cors_config

app = FastAPI(
    root_path="/api/v1",
    title="edu-max Model",
    version="0.0.1",
    redoc_url="/redoc",
    lifespan=app_lifespan,
)

origins = cors_config.CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/health")
async def health_check() -> Response:
    return Response("OK")
