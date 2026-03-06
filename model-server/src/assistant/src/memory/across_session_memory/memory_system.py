# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from typing import Any, Optional

from langchain_naver import ChatClovaX
from weaviate.classes.query import Filter

from assistant.src.memory.across_session_memory.weaviate_memory import WeaviateMemory
from assistant.src.memory.memory_tools import MemoryTool


class MemoryCard:
    def __init__(
        self,
        user_id: str,
        card_id: str,
        links: Optional[list[str]] = None,
        retrieval_count: int = 0,
        last_accessed: Optional[str] = None,
        context: str = "General",
        evolution_history: Optional[list[Any]] = None,
        category: str = "Uncategorised",
    ):
        now = datetime.now().strftime("%Y%m%d%H%M")
        self.user_id = user_id
        self.card_id = card_id
        self.links = links or []
        self.retrieval_count = retrieval_count
        self.last_accessed = last_accessed or now
        self.context = context
        self.evolution_history = evolution_history or []
        self.category = category

    def to_dict(self) -> dict[str, Any]:
        return {
            "links": self.links,
            "retrieval_count": self.retrieval_count,
            "last_accessed": self.last_accessed,
            "context": self.context,
            "evolution_history": self.evolution_history,
            "category": self.category,
        }


class AgenticMemorySystem:
    def __init__(self, cfg: dict, evo_threshold: int = 100):
        self.memories: dict[str, MemoryCard] = {}
        self.vector_db = WeaviateMemory(
            data_server_url=cfg["api-server"]["data-server-url"],
        )
        self.llm = ChatClovaX(
            name="HCX-005",
            api_key=cfg["hcx-005"]["api_key"],
            max_tokens=2048,
        )
        self.memory_tool = MemoryTool(self.llm)
        self.evo_threshold = evo_threshold
        self._evo_cnt = 0

    def __enter__(self):
        print("[MemorySystem] Connected")
        return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        if exit_type is None:
            print("[MemorySystem] Disconnected")
        else:
            print("[MemorySystem] Disconnected due to an error")
            print(f" - Exception: {exit_type.__name__}: {exit_value}")

    def connect_card(self, user_id: str, card_id: str) -> str:
        problem_card = self.vector_db.get("ProblemCard", card_id)
        note = MemoryCard(user_id=user_id, card_id=card_id)

        should_evolve, note = self.process_memory(note, problem_card)
        note_id = self.vector_db.add_memory(note, card_id)
        self.memories[note_id] = note

        if should_evolve:
            self._evo_cnt += 1
            if self._evo_cnt % self.evo_threshold == 0:
                self.consolidate_memories()

        return note_id

    def read(self, memory_id: str):
        memory_card = self.memories.get(memory_id)
        profile = self.vector_db.get("Profile", memory_card.user_id)
        problem_card = self.vector_db.get("ProblemCard", memory_card.card_id)

        return {
            "profile": profile["properties"],
            "memory_card": memory_card.to_dict(),
            "problem_card": problem_card["properties"],
        }

    def delete(self, memory_id: str) -> bool:
        if memory_id in self.memories:
            self.vector_db.delete("Memories", memory_id)
            del self.memories[memory_id]
            return True
        return False

    def consolidate_memories(self):
        for k, m in self.memories.items():
            self.vector_db.add_memory(m.to_dict(), card_id=m.card_id)

    def find_related_memories(self, problem_card, k: int = 5) -> tuple[str, list[int]]:
        if not self.memories:
            return "", []

        response = self.vector_db.search(
            "ProblemCard",
            problem_card["properties"]["question"],
            k,
            target_vector="card_info",
            # TODO: filter 기능 따로 하기
            # filters=Filter.by_property("subject").equal(
            #     problem_card["properties"]["subject"]
            # ),
        )
        response_objects = [
            obj for obj in response if obj["uuid"] != problem_card["uuid"]
        ]

        memory_str = ""
        indices = []

        for i, object in enumerate(response_objects):
            memory_str += f"memory index:{i}\ttalk start time:{datetime.fromisoformat(object['metadata']['creation_time']).strftime('%Y%m%d%H%M')}\tmemory question: {object['properties']['question']}\tmemory context: {object['properties']['context']}\tmemory keywords: {object['properties']['keywords']}\n"
            indices.append(i)

        return memory_str, indices

    def search_agentic(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        if not self.memories:
            return []

        response = self.vector_db.search(
            "ProblemCard", query, k, target_vector="card_info"
        )
        if not response:
            return []

        memories = []
        seen_ids = set()

        for obj in response:
            if obj["uuid"] in seen_ids:
                continue
            memory_dict = {
                "problem_card": obj["properties"],
                "memory_card": self.vector_db.get_memory_card_from_problem_card(
                    obj["uuid"]
                )["properties"],
            }
            memories.append(memory_dict)
            seen_ids.add(obj["uuid"])

        neighbor_count = 0
        for memory in list(memories):
            if neighbor_count >= k:
                break
            links = memory["memory_card"].get("links", "")
            links = list(
                filter(None, (self.vector_db.get_by_question(link) for link in links))
            )
            for link in links:
                if link["uuid"] not in seen_ids and neighbor_count < k:
                    memories.append(
                        {
                            "problem_card": link["properties"],
                            "memory_card": self.vector_db.get_memory_card_from_problem_card(
                                link["uuid"]
                            )[
                                "properties"
                            ],
                        }
                    )
                    seen_ids.add(link["uuid"])
                    neighbor_count += 1

        return memories[:k]

    def process_memory(self, note: MemoryCard, problem_card) -> tuple[bool, MemoryCard]:
        if not self.memories:
            return False, note

        neighbors_text, indices = self.find_related_memories(problem_card, k=5)

        if not indices:
            return False, note

        data = self.memory_tool.evolution_system(
            problem_card, neighbors_text, len(indices)
        )
        if data.get("should_evolve"):
            note.links.extend(data.get("suggested_connections", []))
            return True, note

        return False, note
