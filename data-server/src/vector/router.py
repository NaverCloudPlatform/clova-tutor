# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import os
import tempfile
from typing import Optional, Dict

import aiofiles
from fastapi import APIRouter, File, Form, Request, UploadFile
from pydantic import BaseModel, Field

router = APIRouter()


@router.post("/create")
async def upload_file(
    request: Request,
    index_name: str = Form(...),
    file: UploadFile = File(...),
):

    extension = os.path.splitext(file.filename)[1].lstrip(".").lower()

    tmp_dir = tempfile.TemporaryDirectory()
    tmp_path = os.path.join(tmp_dir.name, f"upload.{extension}")

    size = 0
    async with aiofiles.open(tmp_path, "wb") as out_file:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            await out_file.write(chunk)

    # await asyncio.to_thread(process_file, index_name, tmp_path, extension, tmp_dir)
    process_file(request, index_name, tmp_path, extension, tmp_dir)

    return {"message": "업로드 완료, 백그라운드에서 처리 중입니다."}


def process_file(
    request: Request,
    index_name: str,
    path: str,
    ext: str,
    tmp_dir: tempfile.TemporaryDirectory,
):
    builder = request.app.state.vector_db_manager
    builder.run(index_name, [{"file_path": path, "docs_type": ext}])
    tmp_dir.cleanup()  # 임시 디렉터리 정리


@router.post("/get")
async def get_docs(
    request: Request, index_name: str = Form(...), ids: str | list[str] = Form(...)
):
    builder = request.app.state.vector_db_manager
    response = builder.get(index_name, ids)

    return response


class SearchRequest(BaseModel):
    index_name: str
    query: str = Field(..., description="검색할 쿼리 (예: '피타고라스')")
    search_type: Optional[str] = Field(None, description="검색 방식 (예: 'mmr')")
    k: Optional[int] = Field(None, description="반환할 결과 갯수 (예: 2)")
    filter_property: Optional[str] = Field(
        None, description="filter의 property (예: 'concept')"
    )
    filter_value: Optional[str] = Field(
        None, description="filter의 value (예: '피타고라스 공식')"
    )
    all_of_filters: Optional[Dict[str, str]] = Field(
        None,
        description='AND 조건으로 적용하는 필터셋 (예: {"concept": "피타고라스 공식", "unit": "삼각형"})',
    )


@router.post("/search")
async def search_docs(request: Request, option: SearchRequest):
    filter_obj = None
    if option.filter_property is not None and option.filter_value is not None:
        filter_obj = {"property": option.filter_property, "value": option.filter_value}

    all_of_filters_obj = []
    if option.all_of_filters:
        for _property, _value in option.all_of_filters.items():
            all_of_filters_obj.append({"property": _property, "value": _value})

    retrieve_info = {
        "query": option.query,
        "search_type": option.search_type,
        "k": option.k,
        "filter": (
            all_of_filters_obj if all_of_filters_obj else filter_obj
        ),  # override filter_obj by all_of_filters_obj if both are provided
    }

    builder = request.app.state.vector_db_manager
    response = builder.search(option.index_name, retrieve_info)

    return response


@router.post("/delete")
async def delete_docs(
    request: Request, index_name: str = Form(...), docstore_ids: list[str] = Form(...)
):
    builder = request.app.state.vector_db_manager
    response = builder.remove(index_name, docstore_ids)

    return response


@router.post("/add")
async def add_docs(
    request: Request,
    index_name: str = Form(...),
    file: UploadFile = File(...),
):
    extension = os.path.splitext(file.filename)[1].lstrip(".").lower()

    tmp_dir = tempfile.TemporaryDirectory()
    tmp_path = os.path.join(tmp_dir.name, f"upload.{extension}")

    size = 0
    async with aiofiles.open(tmp_path, "wb") as out_file:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            await out_file.write(chunk)

    builder = request.app.state.vector_db_manager
    response = builder.run(
        index_name, [{"file_path": tmp_path, "docs_type": extension}]
    )
    tmp_dir.cleanup()  # 임시 디렉터리 정리

    return response


class EmbeddingRequest(BaseModel):
    query: str


@router.post("/embedding", response_model=list[float])
async def embed_query(request: Request, body: EmbeddingRequest):
    vector_manager = request.app.state.vector_db_manager
    embeddings: list[float] = vector_manager.embed_query(body.query)

    return embeddings
