# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from urllib.parse import quote

import requests
from langchain_core.messages import AIMessage, HumanMessage

from assistant.src.memory.memory_utils import (
    preprocessing_card_for_weaviate,
    preprocessing_msg_for_weaviate,
)
from assistant.src.schema import ProblemHistory, StudentProfile


class WeaviateMemory:
    def __init__(
        self,
        data_server_url: str = "http://localhost:8000",
        api_prefix: str = "/memory",
        request_timeout: int = 10,
    ):
        self.root_url = data_server_url.rstrip("/")
        self.base_url = f"{self.root_url}{api_prefix}"
        self.request_timeout = request_timeout
        self.references_map = {
            "Chat": "user",
            "ProblemCard": "user",
            "Memories": "card",
        }

    # -------------------------------------------------------------
    # HTTP helper
    # -------------------------------------------------------------
    def _post(self, path: str, payload: dict):
        url = f"{self.base_url}{path}"
        resp = requests.post(url, json=payload, timeout=self.request_timeout)
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str, params: dict | None = None):
        url = f"{self.base_url}{path}"
        resp = requests.get(url, params=params, timeout=self.request_timeout)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str):
        url = f"{self.base_url}{path}"
        resp = requests.delete(url, timeout=self.request_timeout)
        resp.raise_for_status()
        return resp.json()

    # -------------------------------------------------------------
    # public API – Profile / Message / ProblemCard / Memory
    # -------------------------------------------------------------
    def add_profile(self, profile: StudentProfile):
        try:
            res = self._post("/profiles", profile.model_dump())
            return res["uuid"]
        except requests.HTTPError as e:
            # 이미 존재하는 UUID라면 "already exists" 오류 무시
            if e.response is not None and "already exists" in e.response.text:
                return profile.user_id
            raise

    def add_message(self, message: AIMessage | HumanMessage, user_uuid: str):
        msg = preprocessing_msg_for_weaviate(message)
        payload = {
            "properties": {
                "message": msg["message"],
                "image_url": msg["image_url"],
                "type": msg["type"],
            },
            "vector": {"message": self._embedding(msg["message"])},
            "references": {"user": user_uuid},
        }
        res = self._post("/messages", payload)
        return res["msg_id"]

    def add_problem_card(self, problem_card: ProblemHistory, user_uuid: str):
        parsed_card, card_info = preprocessing_card_for_weaviate(problem_card)
        payload = {
            "parsed_card": parsed_card,
            "vector": {
                "question": self._embedding(parsed_card["question"]),
                "context": self._embedding(parsed_card["context"]),
                "keywords": self._embedding(parsed_card["keywords"]),
                "card_info": self._embedding(card_info),
            },
            "user_uuid": user_uuid,
        }
        res = self._post("/problem-cards", payload)
        return res["card_id"]

    def add_memory(self, note, card_id: str):
        payload = {"note": note.to_dict(), "card_uuid": card_id}
        res = self._post("/memories", payload)
        return res["memory_id"]

    # -------------------------------------------------------------
    # CRUD & Search helpers
    # -------------------------------------------------------------
    def delete(self, index_name: str, uuid_: str):
        self._delete(f"/{index_name}/{uuid_}")

    def get(self, index_name: str, uuid_: str, with_ref: bool = False):
        params = {"with_ref": "true"} if with_ref else None
        res = self._get(f"/{index_name}/{uuid_}", params=params)
        return res["data"]

    def get_by_question(self, question: str):
        safe_q = quote(question, safe="")
        res = self._get(f"/problem-cards/by-question/{safe_q}")
        return res["data"]

    def get_memory_card_from_problem_card(self, card_uuid: str):
        res = self._get(f"/memories/by-card/{card_uuid}")
        return res["data"]

    def search(
        self,
        index_name: str,
        query: str,
        k: int = 5,
        target_vector: str | None = None,
    ):
        payload = {
            "index_name": index_name,
            "near_vector": self._embedding(query),
            "k": k,
            "target_vector": target_vector,
        }
        res = self._post("/search", payload)
        return res["data"]["objects"]

    # -------------------------------------------------------------
    # Admin helpers
    # -------------------------------------------------------------
    def delete_collection(self, index_name: str):
        self._delete(f"/collections/{index_name}")

    def setup_collections(self):
        self._post("/collections/setup", {})

    # -------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------
    def _embedding(self, text: str) -> list[float]:
        url = f"{self.root_url}/vector/embedding"
        resp = requests.post(url, json={"query": text}, timeout=self.request_timeout)
        resp.raise_for_status()
        return resp.json()
