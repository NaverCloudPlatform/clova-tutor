# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from assistant_adapter.domain.assistant_entry import AssistantEntry
from assistant_adapter.database._in_assistant_storage import _InMemoryAssistantStorage
from assistant_adapter.domain.edu_assistant import EduAssistant


class AssistantRepository:
    def __init__(self, registry: _InMemoryAssistantStorage):
        self.registry = registry

    async def get(self, chat_id: int) -> AssistantEntry:
        entry = self.registry.get(chat_id)
        return entry

    async def create(self, entry: AssistantEntry) -> AssistantEntry:
        return self.registry.register(entry.assistant.chat_id, entry)

    async def delete(self, chat_id: int) -> None:
        return self.registry.remove(chat_id)
