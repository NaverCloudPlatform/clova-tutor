# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

import pytest

from httpx import AsyncClient

BASE_URL = "/api/v1/users"

#########################################
## user 조회 관련
#########################################


@pytest.mark.asyncio
async def test_get_users(async_client: AsyncClient) -> None:
    res = await async_client.get(BASE_URL)
    assert res.status_code == 200


#########################################
## user 생성 관련
#########################################

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient) -> None:
    # Given: 입력 데이터
    payload = {
        "name": "string",
        "grade": 10,
        "memo": "string"
    }

    # When: POST 요청
    res = await async_client.post(BASE_URL, json=payload)

    # Then: 성공적으로 생성되었는지 확인
    assert res.status_code == 201

    data = res.json()

    # 1) id가 UUID 형식인지 검증
    assert "id" in data
    uuid_obj = uuid.UUID(data["id"])  # 변환 실패 시 ValueError 발생
    assert str(uuid_obj) == data["id"]

    # 2) 값 일치 여부 확인
    assert data["name"] == payload["name"]
    assert data["grade"] == payload["grade"]
    assert data["memo"] == payload["memo"]

@pytest.mark.asyncio
async def test_create_user_with_nullable_memo(async_client: AsyncClient) -> None:
    # Given: memo를 생략하거나 None으로 설정
    payload = {
        "name": "string",
        "grade": 0,
        "memo": None,
    }

    # When: POST 요청
    res = await async_client.post(BASE_URL, json=payload)

    # Then
    assert res.status_code == 201

    data = res.json()

    # id는 UUID 형식
    uuid_obj = uuid.UUID(data["id"])
    assert str(uuid_obj) == data["id"]

    # memo가 null로 들어갔는지 확인
    assert data["memo"] is None
    assert data["name"] == payload["name"]
    assert data["grade"] == payload["grade"]

#########################################
## user 수정 관련
#########################################

@pytest.mark.asyncio
@pytest.fixture
async def test_user_id(async_client: AsyncClient) -> str:
    """테스트용 사용자 생성 후 ID 반환"""
    payload = {
        "name": "initial_name",
        "grade": 1,
        "memo": "initial memo"
    }
    res = await async_client.post(BASE_URL, json=payload)
    assert res.status_code == 201
    return str(res.json()["id"])

@pytest.mark.asyncio
async def test_update_user_name_only(async_client: AsyncClient, test_user_id: str):
    payload = {"name": "new_name"}
    res = await async_client.patch(f"{BASE_URL}/{test_user_id}", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "new_name"
    assert data["id"] == test_user_id
    # 그대로인지 확인
    assert data["grade"] == 1
    assert data["memo"] == "initial memo"

@pytest.mark.asyncio
async def test_update_user_grade_and_memo(async_client: AsyncClient, test_user_id: str):
    payload = {"grade": 5, "memo": None}
    res = await async_client.patch(f"{BASE_URL}/{test_user_id}", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["grade"] == 5
    assert data["memo"] is None
    assert data["name"] == "initial_name"

@pytest.mark.asyncio
async def test_update_user_not_found(async_client: AsyncClient):
    payload = {"name": "fail_case"}
    invalid_id = "00000000-0000-0000-0000-000000000000"
    res = await async_client.patch(f"{BASE_URL}/{invalid_id}", json=payload)
    assert res.status_code == 404

#########################################
## user 삭제 관련
#########################################

@pytest.mark.asyncio
async def test_delete_user_success(async_client: AsyncClient) -> None:
    # Given: 유저 하나 생성
    payload = {"name": "string", "grade": 0, "memo": "string"}
    create_res = await async_client.post(BASE_URL, json=payload)
    assert create_res.status_code == 201
    user_id = create_res.json()["id"]

    # When: 해당 유저 삭제 요청
    delete_res = await async_client.delete(f"{BASE_URL}/{user_id}")

    # Then: 성공적으로 삭제되어야 함
    assert delete_res.status_code == 204
    assert delete_res.text == ""  # No Content 이므로 body 없음


@pytest.mark.asyncio
async def test_delete_user_not_found(async_client: AsyncClient) -> None:
    # Given: 존재하지 않는 UUID
    fake_user_id = str(uuid.uuid4())

    # When: DELETE 요청
    delete_res = await async_client.delete(f"{BASE_URL}/{fake_user_id}")

    # Then: 404 반환
    assert delete_res.status_code == 404
    data = delete_res.json()

    # ErrorResponse 구조 검증
    assert "detail" in data

#########################################
## user 전체 시나리오 테스트
#########################################

@pytest.mark.asyncio
async def test_get_user_scenario(async_client: AsyncClient) -> None:
    # 1) 전체 유저 조회
    res_all = await async_client.get(BASE_URL)
    assert res_all.status_code == 200
    all_users = res_all.json()
    assert isinstance(all_users, list)

    # 2) 테스트용 유저 생성
    payload = {"name": "test_user", "grade": 1, "memo": "optional"}
    create_res = await async_client.post(BASE_URL, json=payload)
    assert create_res.status_code == 201
    created_user = create_res.json()
    user_id = created_user["id"]

    # 3) 특정 유저 조회
    res_one = await async_client.get(f"{BASE_URL}/{user_id}")
    assert res_one.status_code == 200
    user_data = res_one.json()

    # 4) 반환값 검증
    assert user_data["id"] == user_id
    assert user_data["name"] == payload["name"]
    assert user_data["grade"] == payload["grade"]
    assert user_data["memo"] == payload["memo"]

    # 5) 삭제
    delete_res = await async_client.delete(f"{BASE_URL}/{user_id}")
    assert delete_res.status_code == 204
    assert delete_res.text == ""
