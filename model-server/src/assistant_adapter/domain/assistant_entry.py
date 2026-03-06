# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio

from typing import TYPE_CHECKING

from datetime import datetime
from assistant_adapter.domain.edu_assistant import EduAssistant

if TYPE_CHECKING:
    from assistant_adapter.database.assistant_repository import AssistantRepository


class AssistantEntry:
    def __init__(
        self,
        assistant: EduAssistant,
        repository: "AssistantRepository",
    ) -> None:
        self.assistant = assistant
        self.repo = repository
        self.timer: asyncio.Task | None = None
        self.last_used: datetime = datetime.now()

    # 호출될 때마다 실행
    def touch(self) -> None:
        self.last_used = datetime.now()
        self._reschedule_timer()

    # 타이머 재설정
    def _reschedule_timer(self) -> None:
        # 예전 타이머 취소
        if self.timer and not self.timer.done():
            self.timer.cancel()

        # 새로운 타이머 설정
        self.timer = asyncio.create_task(self._delayed_save())

    # 1시간 후 메모리 저장
    async def _delayed_save(self) -> None:
        try:
            await asyncio.sleep(3600)  # 1h
            self.assistant.save_long_term_memory()

            await self.repo.delete(self.assistant.chat_id)
        except asyncio.CancelledError:
            # 재호출로 인해 취소된 경우 무시
            return
        except Exception as e:
            # 저장 실패 → 로깅 정도만
            print(f"[AssistantEntry] memory save failed: {e}")
            # 기존 로직 유지
            await self.repo.delete(self.assistant.chat_id)
