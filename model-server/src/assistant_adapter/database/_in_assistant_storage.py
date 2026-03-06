# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from __future__ import annotations
from typing import ClassVar, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from assistant_adapter.domain.assistant_entry import AssistantEntry


class _InMemoryAssistantStorage:
    """chat_id <-> EduAssistant 캐시"""

    _instance: ClassVar[Optional["_InMemoryAssistantStorage"]] = None

    def __init__(self) -> None:
        self._assistants: dict[int, AssistantEntry] = {}

    @classmethod
    def instance(cls) -> "_InMemoryAssistantStorage":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get(self, chat_id: int) -> AssistantEntry | None:
        entry = self._assistants.get(chat_id)
        return entry if entry else None

    def register(
        self,
        chat_id: int,
        entry: AssistantEntry,
    ) -> AssistantEntry:
        self._assistants[chat_id] = entry
        return self._assistants[chat_id]

    # 내부 전용: save 완료 뒤 캐시 제거
    def remove(self, chat_id: int) -> None:
        self._assistants.pop(chat_id, None)


assistant_storage = _InMemoryAssistantStorage.instance()
