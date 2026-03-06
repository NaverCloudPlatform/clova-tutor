# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


import pytest

from httpx import AsyncClient

from tests.utils import assert_structure

BASE_URL = "/api/v1/problems"

TEST_PROBLEM = {
    "id": "E3-M-001",
    "subject": "math",
    "grade": 3,
    "type": "단일응답 주관식",
    "category": "세 자리 수의 덧셈 계산",
    "level": 1,
    "url": None,
    "semester": None,
    "primary": "수와 연산",
    "secondary": "덧셈과 뺄셈",
    "specific": "세 자리 수의 덧셈",
    "problem": "345 + 276의 값을 구하세요.",
    "choices": None,
    "correct_answers": [
    {
        "answer": "621",
        "accepted_answers": [
        "621.",
        "621 "
        ]
    }
    ],
    "explanation": None,
    "hint": None,
    "tags": None
}

TEST_SKELETON = """
    {
  "id": "string",
  "content": {
    "subject": "string",
    "grade": 0,
    "semester": 0,
    "level": 0,
    "primary": "string",
    "secondary": "string",
    "specific": "string",
    "category": "string",
    "problem": "string",
    "tags": [
      "string"
    ],
    "hint": "string",
    "explanation": "string",
    "choices": []
  }
}
"""


@pytest.mark.asyncio
async def test_problem(async_client: AsyncClient) -> None:
    # 1. 문제 생성
    creation_payload = {
        "problems": [
            TEST_PROBLEM
        ]
    }

    res_create = await async_client.post(f"{BASE_URL}", json=creation_payload)

    assert res_create.status_code == 200

    created_data = res_create.json()
    assert "ids" in created_data
    assert isinstance(created_data["ids"], list)
    assert len(created_data["ids"]) > 0

    problem_id = created_data["ids"][0]

    # 2. 문제 조회
    res = await async_client.get(f"{BASE_URL}/{problem_id}")
    assert res.status_code == 200

    problem_detail = res.json()
    assert isinstance(problem_detail, dict)
    assert "id" in problem_detail
    assert "content" in problem_detail

    skeleton = TEST_SKELETON

    assert_structure(problem_detail ,skeleton)
