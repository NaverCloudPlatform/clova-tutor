# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import pytest

from httpx import AsyncClient

from tests.utils import assert_structure

BASE_URL = "/api/v1/chats"


## 추후 auth 로 이동
@pytest.mark.asyncio
async def test_access_without_header(async_client: AsyncClient):
    res = await async_client.get(BASE_URL)
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_access_with_wrong_header(async_client: AsyncClient):
    headers = {"X-User-Id" : "Invalid-UUID"}
    res = await async_client.get(BASE_URL, headers=headers)
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_get_chat_invalid_cases(async_client: AsyncClient) -> None:
    """
    Chat 조회 테스트
    - 성공 케이스
    - 없는 chat_id 접근
    - 다른 사람의 chat_id 접근
    """

    # 유저 생성
    user_payload = {"name": "test1", "grade": 10, "memo": None}
    res = await async_client.post("/api/v1/users", json=user_payload)
    assert res.status_code == 201
    user_id = res.json()["id"]

    headers = {"X-User-Id": str(user_id)}

    # 채팅 생성
    chat_payload = {"title": "chat1", "subject": "math", "grade": "10"}
    chat_res = await async_client.post(BASE_URL, json=chat_payload, headers=headers)
    assert chat_res.status_code == 201
    chat_id = chat_res.json()["id"]

    # 1. 성공 케이스
    detail_res = await async_client.get(f"{BASE_URL}/{chat_id}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == chat_id

    # 2. 없는 chat_id
    res = await async_client.get(f"{BASE_URL}/999999", headers=headers)
    assert res.status_code == 404

    # 3. 다른 사람의 chat_id 접근 → 403 Forbidden
    # 새로운 유저 생성
    other_payload = {"name": "test2", "grade": 11, "memo": None}
    other_res = await async_client.post("/api/v1/users", json=other_payload)
    assert other_res.status_code == 201
    other_user_id = other_res.json()["id"]

    other_headers = {"X-User-Id": str(other_user_id)}

    res = await async_client.get(f"{BASE_URL}/{chat_id}", headers=other_headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_chat_invalid_cases(async_client: AsyncClient) -> None:
    """
    Chat 생성 테스트
    - 성공 케이스
    - subject 가 math/english 가 아닌 경우
    - grade 예외 처리 (현재 없음)
    - Title 100자 넘었을 때
    """

    # 유저 생성
    user_payload = {"name": "test1", "grade": 10, "memo": None}
    res = await async_client.post("/api/v1/users", json=user_payload)
    assert res.status_code == 201
    user_id = res.json()["id"]
    headers = {"X-User-Id": str(user_id)}

    # 1. 성공 케이스
    chat_payload = {"title": "valid chat", "subject": "math", "grade": "10"}
    res = await async_client.post(BASE_URL, json=chat_payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "valid chat"
    assert data["subject"] == "math"

    # 2. subject 가 math/english 가 아닌 경우
    invalid_payload = {"title": "wrong subject", "subject": "history", "grade": 10}
    res = await async_client.post(BASE_URL, json=invalid_payload, headers=headers)
    assert res.status_code == 422  # FastAPI/Pydantic validation error

    # 3. grade 예외 처리 (현재 없음 → 나중에 비즈니스 로직에서 막을 수 있음)
    # invalid_payload = {"title": "wrong grade", "subject": "math", "grade": "999"}
    # res = await async_client.post(BASE_URL, json=invalid_payload, headers=headers)
    # # 현재 grade 예외처리 없음 → 201 로 들어갈 수도 있음 -> 추후 수정 필요
    # assert res.status_code in (201, 422)

    # 4. Title 100자 넘었을 때
    too_long_title = "a" * 101
    invalid_payload = {"title": too_long_title, "subject": "english", "grade": "10"}
    res = await async_client.post(BASE_URL, json=invalid_payload, headers=headers)
    assert res.status_code == 422  # Pydantic Field(max_length=100) 같은 제약 걸렸다고 가정


@pytest.mark.asyncio
async def test_update_chat(async_client: AsyncClient) -> None:
    """
    Chat 수정 테스트
    - 성공 케이스
    - 없는 chat_id 수정
    - 다른 사람의 chat 수정
    - Title 100자 넘었을 때
    """

    # 유저 생성
    user_payload = {"name": "user1", "grade": 10, "memo": None}
    res = await async_client.post("/api/v1/users", json=user_payload)
    assert res.status_code == 201
    user_id = res.json()["id"]
    headers = {"X-User-Id": str(user_id)}

    # 채팅 생성
    chat_payload = {"title": "chat1", "subject": "math", "grade": "10"}
    res = await async_client.post(BASE_URL, json=chat_payload, headers=headers)
    assert res.status_code == 201
    chat_id = res.json()["id"]

    # 1. 성공 케이스
    update_payload = {"title": "chat1-updated"}
    res = await async_client.patch(f"{BASE_URL}/{chat_id}", json=update_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "chat1-updated"

    # 2. 없는 chat_id 수정
    res = await async_client.patch(f"{BASE_URL}/999999", json={"title": "not-exist"}, headers=headers)
    assert res.status_code == 404

    # 3. 다른 사람의 chat 수정
    # 새로운 유저 생성
    other_payload = {"name": "user2", "grade": 11, "memo": None}
    other_res = await async_client.post("/api/v1/users", json=other_payload)
    other_user_id = other_res.json()["id"]
    other_headers = {"X-User-Id": str(other_user_id)}

    res = await async_client.patch(f"{BASE_URL}/{chat_id}", json={"title": "hacker"}, headers=other_headers)
    assert res.status_code == 403

    # 4. Title 100자 넘었을 때
    too_long_title = "a" * 101
    res = await async_client.patch(f"{BASE_URL}/{chat_id}", json={"title": too_long_title}, headers=headers)
    assert res.status_code == 422  # Pydantic validation 실패


@pytest.mark.asyncio
async def test_delete_chat(async_client: AsyncClient) -> None:
    """
    Chat 삭제 테스트
    - 성공 케이스
    - 없는 chat_id 삭제
    - 다른 사람의 chat 삭제
    """

    # 유저 생성
    user_payload = {"name": "deleter", "grade": 9, "memo": None}
    res = await async_client.post("/api/v1/users", json=user_payload)
    user_id = res.json()["id"]
    headers = {"X-User-Id": str(user_id)}

    # 채팅 생성
    chat_payload = {"title": "chat-to-delete", "subject": "english", "grade": "10"}
    res = await async_client.post(BASE_URL, json=chat_payload, headers=headers)
    chat_id = res.json()["id"]

    # 1. 성공 케이스
    res = await async_client.delete(f"{BASE_URL}/{chat_id}", headers=headers)
    assert res.status_code == 204  # 삭제 성공은 보통 204 No Content

    # 2. 없는 chat_id 삭제
    res = await async_client.delete(f"{BASE_URL}/999999", headers=headers)
    assert res.status_code == 404

    # 3. 다른 사람의 chat 삭제
    # 유저2 생성
    other_payload = {"name": "user2", "grade": 8, "memo": None}
    other_res = await async_client.post("/api/v1/users", json=other_payload)
    other_user_id = other_res.json()["id"]
    other_headers = {"X-User-Id": str(other_user_id)}

    # 유저1이 새 채팅 생성
    res = await async_client.post(BASE_URL, json={"title": "victim", "subject": "math", "grade": "10"}, headers=headers)
    victim_chat_id = res.json()["id"]

    # 유저2가 삭제 시도
    res = await async_client.delete(f"{BASE_URL}/{victim_chat_id}", headers=other_headers)
    assert res.status_code == 403


## 성공 시나리오만 테스트
@pytest.mark.asyncio
async def test_create_get_update_delete_chat(async_client: AsyncClient):
    """
    성공 케이스 테스트
    1. 유저 생성
    2. 채팅 생성
    3. 채팅 조회
    4. 타이틀 수정
    5. 채팅 조회
    6. 채팅 삭제
    """

    # 1.
    payload = {
        "name": "test1",
        "grade": 10,
        "memo": None
    }
    res = await async_client.post("/api/v1/users", json=payload)
    assert res.status_code == 201

    user_id = res.json()["id"]


    # 2. 채팅 생성
    headers = {"X-User-Id" : user_id}

    # Given
    chat_payload = {
        "title" : "test",
        "subject" : "math",
        "grade": "10"
    }

    # Validate
    skeleton = {
        "title": "string",
        "subject": "string",
        "id": 0,
        "has_problem": False,
        "has_active_goal": False
        }

    chat_create_res = await async_client.post(f"{BASE_URL}", json=chat_payload, headers=headers)
    assert chat_create_res.status_code == 201
    data= chat_create_res.json()
    assert_structure(data, skeleton)
    # 초기 생성 값이니 항상 False 이어야 함
    assert not data["has_problem"]
    assert not data["has_active_goal"]

    # 추후 사용을 위해 저장
    chat_id = data.get("id")

    # 3. 채팅 전체 조회
    chat_list_res = await async_client.get(f"{BASE_URL}", headers=headers)

    assert chat_list_res.status_code == 200

    data = chat_list_res.json()

    assert len(data["items"]) == 1

    # 4. 타이틀 수정
    update_payload = {
        "title" : "test2"
    }
    chat_update_res = await async_client.patch(f"{BASE_URL}/{chat_id}",json=update_payload,headers=headers)
    assert chat_update_res.status_code == 200

    update_data =chat_update_res.json()
    assert_structure(update_data, skeleton)
    assert update_data["title"] == update_payload["title"]

    # 5. 채팅 상세 조회
    chat_detail_res = await async_client.get(f"{BASE_URL}/{chat_id}", headers=headers)
    assert chat_detail_res.status_code == 200
    detail_data = chat_detail_res.json()
    assert_structure(detail_data, skeleton)
    assert detail_data["title"] == "test2"

    # 6. 채팅 삭제
    chat_delete_res = await async_client.delete(f"{BASE_URL}/{chat_id}", headers=headers)
    assert chat_delete_res.status_code == 204

    # 삭제 후 재조회 → 404 이어야 함
    chat_detail_res = await async_client.get(f"{BASE_URL}/{chat_id}", headers=headers)
    assert chat_detail_res.status_code == 404







