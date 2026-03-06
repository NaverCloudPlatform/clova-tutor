# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid
from dataclasses import asdict

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from starlette import status
from weaviate.classes.config import Configure, DataType, Property, ReferenceProperty
from weaviate.classes.query import Filter, QueryReference, MetadataQuery
from weaviate.client import WeaviateClient

from memory.entities.schemas import (
    StudentProfile,
    MessagePayload,
    MemoryPayload,
    ProblemCardPayload,
    GetResp,
    DeleteResp,
    SearchPayload,
    SetupResp,
)

router = APIRouter()


@router.post(
    "/profiles",
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(request: Request, profile: StudentProfile):
    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get("Profile")
    try:
        uid = db.data.insert(
            properties={
                "name": profile.name,
                "semester": profile.semester,
                "grade": profile.grade,
            },
            uuid=uuid.UUID(profile.user_id),
        )
        return {"uuid": uid}
    except Exception as e:
        import logging

        logging.error(e)
        raise HTTPException(500, str(e))


@router.post(
    "/messages",
    status_code=status.HTTP_201_CREATED,
)
async def add_message(request: Request, msg: MessagePayload):
    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get("Chat")

    try:
        msg_id = db.data.insert(
            properties=msg.properties.model_dump(),
            vector=msg.vector.model_dump(),
            references=msg.references.model_dump(),
        )
        return {"msg_id": msg_id}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post(
    "/problem-cards",
    status_code=status.HTTP_201_CREATED,
)
async def add_problem_card(request: Request, card: ProblemCardPayload):
    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get("ProblemCard")

    try:
        card_id = db.data.insert(
            properties=card.parsed_card,
            vector=card.vector,
            references={"user": card.user_uuid},
        )
        return {"card_id": card_id}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post(
    "/memories",
    status_code=status.HTTP_201_CREATED,
)
async def add_memory(request: Request, mem: MemoryPayload):
    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get("Memories")

    try:
        memory_id = db.data.insert(
            properties=mem.note,
            references={"card": mem.card_uuid},
        )
        return {"memory_id": memory_id}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{collection}/{item_uuid}", response_model=GetResp)
async def fetch_object(
    request: Request,
    collection: str,
    item_uuid: str,
    with_ref: bool = Query(False, description="참조를 함께 반환할지 여부"),
):
    references_map = {
        "Chat": "user",
        "ProblemCard": "user",
        "Memories": "card",
    }

    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get(collection)

    try:
        obj = (
            db.query.fetch_object_by_id(
                item_uuid,
                return_references=QueryReference(link_on=references_map[collection]),
            )
            if with_ref
            else db.query.fetch_object_by_id(item_uuid)
        )
        if obj is None:
            raise HTTPException(status_code=404, detail="Not Found")
        obj_dict = asdict(obj)
        return {"data": obj_dict}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.delete("/{collection}/{item_uuid}", response_model=DeleteResp)
async def delete_object(request: Request, collection: str, item_uuid: str):
    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get(collection)
    try:
        db.data.delete_by_id(item_uuid)
        return {"deleted": True}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/problem-cards/by-question/{question}", response_model=GetResp)
async def get_by_question(request: Request, question: str):
    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get("ProblemCard")
    try:
        res = db.query.fetch_objects(
            filters=Filter.by_property("question").equal(question)
        )
        if not res or not res.objects:
            raise HTTPException(404, "Not Found")
        return {"data": res.objects[0]}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/memories/by-card/{card_uuid}", response_model=GetResp)
async def get_memory_from_card(request: Request, card_uuid: str):
    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get("Memories")
    try:
        res = db.query.fetch_objects(
            filters=Filter.by_ref("card").by_id().equal(card_uuid)
        )
        if not res or not res.objects:
            raise HTTPException(404, "Not Found")
        return {"data": res.objects[0]}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/search", response_model=GetResp)
async def search_objects(request: Request, payload: SearchPayload):
    references_map = {
        "Chat": "user",
        "ProblemCard": "user",
        "Memories": "card",
    }

    client = request.app.state.vector_db_manager.weaviate_client
    db = client.collections.get(payload.index_name)
    try:
        res = db.query.near_vector(
            near_vector=payload.near_vector,
            limit=payload.k,
            target_vector=payload.target_vector,
            return_metadata=MetadataQuery(creation_time=True, distance=True),
            return_references=QueryReference(
                link_on=references_map[payload.index_name]
            ),
        )
        obj_dict = jsonable_encoder(res)
        return {"data": obj_dict}
    except Exception as e:
        print(str(e))
        raise HTTPException(500, str(e))


@router.delete("/collections/{collection_name}", response_model=DeleteResp)
async def delete_collection(request: Request, collection_name: str):
    client: WeaviateClient = request.app.state.vector_db_manager.weaviate_client
    try:
        # client.collections.delete(collection_name)
        client.schema.delete_class(collection_name)
        return {"deleted": True}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/collections/setup", response_model=SetupResp, tags=["admin"])
async def setup_collections(request: Request):
    """
    존재하지 않는 경우에만 Profile / Chat / ProblemCard / Memories 컬렉션 생성
    """
    client = request.app.state.vector_db_manager.weaviate_client

    def _maybe_create(name: str, **kwargs):
        try:
            client.collections.get(name)  # 존재 검사
        except Exception:
            client.collections.create(name, **kwargs)

    # Profile
    _maybe_create(
        "Profile",
        properties=[
            Property(name="name", data_type=DataType.TEXT),
            Property(name="semester", data_type=DataType.TEXT),
            Property(name="grade", data_type=DataType.INT),
        ],
    )

    # Chat
    _maybe_create(
        "Chat",
        properties=[
            Property(name="message", data_type=DataType.TEXT),
            Property(name="image_url", data_type=DataType.TEXT),
            Property(name="type", data_type=DataType.TEXT),
        ],
        references=[ReferenceProperty(name="user", target_collection="Profile")],
        vectorizer_config=[Configure.NamedVectors.none(name="message")],
    )

    # ProblemCard
    _maybe_create(
        "ProblemCard",
        properties=[
            Property(name="question", data_type=DataType.TEXT),
            Property(name="explanation", data_type=DataType.TEXT),
            Property(name="answer", data_type=DataType.TEXT),
            Property(name="level", data_type=DataType.INT),
            Property(name="data_source", data_type=DataType.TEXT),
            Property(name="has_image", data_type=DataType.BOOL),
            Property(name="image_url", data_type=DataType.TEXT),
            Property(name="context", data_type=DataType.TEXT),
            Property(name="keywords", data_type=DataType.TEXT),
        ],
        references=[ReferenceProperty(name="user", target_collection="Profile")],
        vectorizer_config=[
            Configure.NamedVectors.none(name="question"),
            Configure.NamedVectors.none(name="context"),
            Configure.NamedVectors.none(name="keywords"),
            Configure.NamedVectors.none(name="card_info"),
        ],
    )

    # Memories
    _maybe_create(
        "Memories",
        properties=[
            Property(name="links", data_type=DataType.TEXT_ARRAY),
            Property(name="retrieval_count", data_type=DataType.INT),
            Property(name="last_accessed", data_type=DataType.TEXT),
            Property(name="evolution_history", data_type=DataType.TEXT_ARRAY),
            Property(name="category", data_type=DataType.TEXT),
        ],
        references=[ReferenceProperty(name="card", target_collection="ProblemCard")],
    )

    return {"created": True}
