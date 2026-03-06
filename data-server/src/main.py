# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import FastAPI, Response
from starlette.middleware.cors import CORSMiddleware

from config.lifespan import app_lifespan
from memory.router import router as memory_router
from vector.router import router as weaviate_router

app = FastAPI(
    root_path="/api/v1",
    title="edu-max Data",
    version="0.0.1",
    redoc_url="/redoc",
    lifespan=app_lifespan,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(weaviate_router, prefix="/vector", tags=["vector"])
app.include_router(memory_router, prefix="/memory", tags=["memory"])


@app.get("/health")
async def health_check() -> Response:
    return Response("OK")