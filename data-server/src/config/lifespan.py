# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from contextlib import asynccontextmanager

from fastapi import FastAPI

from common.logging import set_logger
from vector.service import VectorDBManager


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    try:
        logger = set_logger("VectorDBManager", "DEBUG")
        app.state.vector_db_manager = VectorDBManager(logger=logger)
        yield

    finally:
        app.state.vector_db_manager.close()
        await app.state.mysql.close()
