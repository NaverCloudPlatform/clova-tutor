# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
import uuid

from langchain_core.messages import AIMessage, HumanMessage
from redis.cluster import RedisCluster

from assistant.src.schema import ProblemHistory


class RedisMemory:
    def __init__(self, redis_client: RedisCluster):
        self.client = redis_client

    def _save_message_to_namespace(
        self, namespace: str, user_id: str, message: AIMessage | HumanMessage
    ):
        key = f"{namespace}:{user_id}"
        self.client.rpush(key, message.model_dump_json())

    def _get_messages_from_namespace(self, namespace: str, user_id: str):
        key = f"{namespace}:{user_id}"
        messages = self.client.lrange(key, 0, -1)

        return [json.loads(meg) for meg in messages]

    def _clear_namespace(self, namespace: str, user_id: str):
        key = f"{namespace}:{user_id}"
        self.client.delete(key)

    # Chat Management
    def save_to_chat_message(self, user_id: str, message: AIMessage | HumanMessage):
        self._save_message_to_namespace("chat", user_id, message)

    def get_chat_history(self, user_id):
        return self._get_messages_from_namespace("chat", user_id)

    def clear_chat_history(self, user_id):
        self._clear_namespace("chat", user_id)

    # In Memory
    def save_to_in_memory(self, user_id: str, message: AIMessage | HumanMessage):
        self._save_message_to_namespace("in-memory", user_id, message)

    def get_in_memory(self, user_id):
        return self._get_messages_from_namespace("in-memory", user_id)

    def clear_in_memory(self, user_id):
        self._clear_namespace("in-memory", user_id)

    # Problem Card Management
    # TODO: content를 Problem_Info로 변경
    def save_problem_card(
        self,
        user_id: str,
        content: ProblemHistory,
        messages: list[HumanMessage | AIMessage],
    ):
        card_id = str(uuid.uuid4())
        card_key = f"problem_card:{user_id}:{card_id}"
        serialized = [
            (
                {"type": "human", "content": m.content}
                if isinstance(m, HumanMessage)
                else {"type": "ai", "content": m.content}
            )
            for m in messages
        ]
        card_data = {
            "content": content.model_dump_json(),
            "messages": json.dumps(serialized),
        }
        self.client.hset(card_key, mapping=card_data)
        self.client.rpush(f"problem_card_index:{user_id}", card_id)

        return card_id

    def get_problem_card(self, user_id: str, card_id: str):
        key = f"problem_card:{user_id}:{card_id}"
        problem_card = self.client.hgetall(key)

        raw_messages = json.loads(problem_card["messages"])
        messages = []
        for m in raw_messages:
            if m["type"] == "human":
                messages.append(HumanMessage(content=m["content"]))
            elif m["type"] == "ai":
                messages.append(AIMessage(content=m["content"]))
            else:
                raise ValueError(f"Unknown message type: {m['type']}")

        problem_card["messages"] = messages
        problem_card["content"] = ProblemHistory.model_validate_json(
            problem_card["content"]
        )

        return problem_card if problem_card else None

    def get_all_problem_cards(self, user_id: str):
        index_key = f"problem_card_index:{user_id}"
        card_ids = self.client.lrange(index_key, 0, -1)
        cards = [self.get_problem_card(user_id, cid) for cid in card_ids]

        return cards

    def delete_problem_cards(self, user_id: str):
        self._clear_namespace("problem_card", user_id)
        self._clear_namespace("problem_card_index", user_id)

    # Profile Management
    def add_user_profile(self, user_id: str, profile_data: dict):
        key = f"profile:{user_id}"
        self.client.hset(key, mapping=profile_data)

    def get_user_profile(self, user_id: str):
        return self.client.hgetall(f"profile:{user_id}")

    def update_user_profile_field(self, user_id: str, field: str, value: str):
        self.client.hset(f"profile:{user_id}", field, value)

    def delete_user_profile(self, user_id: str):
        self._clear_namespace("profile", user_id)

    # Namespace / Cleanup
    def clear_namespace_by_prefix(self, namespace_prefix: str):
        keys = list(self.client.scan_iter(f"{namespace_prefix}*"))
        if keys:
            self.client.delete(*keys)
            print(f"Deleted {len(keys)} keys from namespace '{namespace_prefix}'")
        else:
            print(f"No keys found for namespace '{namespace_prefix}'")

    # Test Only
    def delete_all_for_user(self, user_id: str):
        for prefix in [
            "chat",
            "in-memory",
            "problem_card",
            "problem_card_index",
            "profile",
        ]:
            self.clear_namespace_by_prefix(f"{prefix}:{user_id}")
