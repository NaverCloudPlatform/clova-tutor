# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from httpx import AsyncClient

BASE_URL = "/api/v1/users"

# 기본 유저 세팅
@pytest_asyncio.fixture(scope="function")
async def test_user(async_client: AsyncClient) -> AsyncGenerator[str, None]:
    payload = {
        "name": "Alice",
        "grade": 1,
        "memo": "alpha"
    }
    res = await async_client.post(BASE_URL, json=payload)
    assert res.status_code == 201
    user_id = res.json()["id"]

    # yield로 반환
    yield user_id

    # 필요 시, fixture 종료 시점에 cleanup
    await async_client.delete(f"{BASE_URL}/{user_id}")

#########################################
## 이해하지 못한 개념 조회 테스트
#########################################

@pytest.mark.asyncio
async def test_get_unknown_concepts_list(async_client: AsyncClient, test_user: str):
    """
    특정 사용자의 이해하지 못한 개념 목록 조회 테스트
    """
    # Given: 먼저 개념 하나 생성
    payload = {
        "subject": "수학",
        "key_concept": "삼각함수",
        "unknown_concept": "사인 법칙",
        "unknown_concept_reason": "공식이 이해 안 됨",
    }
    put_res = await async_client.put(
        f"{BASE_URL}/{test_user}/unknown-concepts", json=payload
    )
    assert put_res.status_code == 201

    # When: 목록 조회
    get_res = await async_client.get(
        f"{BASE_URL}/{test_user}/unknown-concepts"
    )

    # Then
    assert get_res.status_code == 200
    data = get_res.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first_item = data[0]
    # 응답 DTO 필드 검증
    assert "id" in first_item
    assert "created_at" in first_item
    assert "updated_at" in first_item
    assert first_item["subject"] == "수학"
    assert first_item["key_concept"] == "삼각함수"
    assert first_item["unknown_concept"] == "사인 법칙"
    assert first_item["unknown_concept_reason"] == "공식이 이해 안 됨"


@pytest.mark.asyncio
async def test_get_unknown_concepts_list_with_subject_filter(async_client: AsyncClient, test_user: str):
    """
    subject 필터링 테스트
    """
    # When: subject 필터링으로 조회
    res = await async_client.get(
        f"{BASE_URL}/{test_user}/unknown-concepts",
        params={"subject": "수학"},
    )

    # Then
    assert res.status_code == 200
    data = res.json()
    assert all(item["subject"] == "수학" for item in data)


#########################################
## 이해하지 못한 개념 시나리오 테스트
#########################################

@pytest.mark.asyncio
async def test_unknown_concepts_crud_scenario(async_client: AsyncClient, test_user: str):
    """
    1) 비어있을 때 조회
    2) 새로운 unknown concept 생성
    3) 생성된 unknown concept 조회
    4) 삭제 후, 정상 삭제 확인
    """
    user_id = test_user

    # 1.
    get_res_init = await async_client.get(
        f"/users/{user_id}/unknown-concepts",
    )
    assert get_res_init.status_code == 200
    data = get_res_init.json()
    assert isinstance(data, list)  # 리스트인지 확인
    assert len(data) == 0

    # 2.
    payload = {
        "subject": "수학",
        "key_concept": "삼각함수",
        "unknown_concept": "코사인 법칙",
        "unknown_concept_reason": "개념이 어려움",
    }

    create_res = await async_client.put(
        f"/users/{user_id}/unknown-concepts",
        json=payload,
    )

    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["subject"] == payload["subject"]
    assert created_data["key_concept"] == payload["key_concept"]
    assert created_data["unknown_concept"] == payload["unknown_concept"]

    # 3.
    get_res = await async_client.get(
        f"/users/{user_id}/unknown-concepts",
        params={"subject": "수학"},
    )

    assert get_res.status_code == 200
    get_data = get_res.json()
    assert isinstance(get_data, list)
    # 방금 생성한 값이 포함되어야 함
    assert any(
        item["unknown_concept"] == "코사인 법칙"
        for item in get_data
    )

    # 4.
    delete_res = await async_client.delete(
        f"/users/{user_id}/unknown-concepts",
        params={"subject": "수학", "key_concept": "삼각함수"},
    )

    assert delete_res.status_code == 204

    # 삭제 후 조회하면 빈 리스트일 수 있음
    get_res_after_delete = await async_client.get(
        f"/users/{user_id}/unknown-concepts",
        params={"subject": "수학"},
    )
    assert get_res_after_delete.status_code == 200
    get_data_after_delete = get_res_after_delete.json()
    assert all(
        item["key_concept"] != "삼각함수" for item in get_data_after_delete
    )
