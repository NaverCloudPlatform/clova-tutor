# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import requests

from assistant.src.utils.load_utils import load_yaml


class UnknownConceptDB:
    def __init__(self, base_url: str, user_id: str = ""):
        self.user_id = user_id
        self.base_url = base_url

    def list_unknown_concepts(self, subject: str | None = None):
        """
        GET /users/{user_id}/unknown-concepts
        """
        url = f"{self.base_url}/users/{self.user_id}/unknown-concepts"
        params = {}
        if subject:
            params["subject"] = subject

        resp = requests.get(url, params=params)
        return resp.json()  # List[dict]

    def upsert_unknown_concept(
        self,
        subject: str,
        key_concept: str,
        unknown_concept: str,
        unknown_concept_reason: str,
    ):
        """
        POST /users/{user_id}/unknown-concepts
        """
        url = f"{self.base_url}/users/{self.user_id}/unknown-concepts"
        payload = {
            "subject": subject,
            "key_concept": key_concept,
            "unknown_concept": unknown_concept,
            "unknown_concept_reason": unknown_concept_reason,
        }

        resp = requests.put(url, json=payload)
        return resp.json()  # dict

    def delete_unknown_concepts(
        self,
        subject: str | None = None,
        key_concept: str | None = None,
    ):
        """
        DELETE /users/{user_id}/unknown-concepts
        — subject, key_concept 없으면 전체 삭제
        — subject만 주면 subject에 해당하는 전체 삭제
        — subject+key_concept 모두 주면 해당 행만 삭제
        """
        url = f"{self.base_url}/users/{self.user_id}/unknown-concepts"
        params: dict[str, str] = {}
        if subject is not None:
            params["subject"] = subject
        if key_concept is not None:
            params["key_concept"] = key_concept

        resp = requests.delete(url, params=params)
        resp.raise_for_status()
        # 204 No Content 반환 시 resp.text는 빈 문자열
        return resp.status_code


if __name__ == "__main__":

    base_url = load_yaml("assistant/api_info.yaml")["api-server"]["be-server-url"]
    unknown = UnknownConceptDB(
        base_url=base_url, user_id="f97ba8d5-642e-4648-97e7-1df06ff382ee"
    )

    # POST 요청 - 초기 정보 추가
    unknown.upsert_unknown_concept(
        subject="수학",
        key_concept="일차함수",
        unknown_concept="절편, 그래프",
        unknown_concept_reason="문항 2번을 틀림. 튜터와의 대화에서 X 절편의 정의를 전혀 이해하지 못하고 있음",
    )
    unknown.upsert_unknown_concept(
        subject="영어",
        key_concept="어법",
        unknown_concept="to 부정사",
        unknown_concept_reason="to 부정사 문제인 3번을 틀림",
    )

    # GET 요청 - 조회
    concepts = unknown.list_unknown_concepts(subject="영어")
    print("GET 결과:", concepts)

    # POST 요청 - 정보 업데이트
    unknown.upsert_unknown_concept(
        subject="영어",
        key_concept="어법",
        unknown_concept="to 부정사",
        unknown_concept_reason="to 부정사를 조금 이해함",
    )

    # GET 요청 - 업데이트 결과 조회
    concepts = unknown.list_unknown_concepts(subject="영어")
    print("GET 결과:", concepts)

    # GET 요청 - 전체 정보 조회
    concepts = unknown.list_unknown_concepts()
    print("GET 결과:", concepts)

    # GET 요청 - 수학 정보 조회
    concepts = unknown.list_unknown_concepts(subject="수학")
    print("GET 결과:", concepts)

    # GET 요청 - 타 학생 정보 조회
    concepts = unknown.list_unknown_concepts()
    print("GET 결과:", concepts)

    unknown.delete_unknown_concepts()
