# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from chats.domain.assistant.assistant_request import AssistantRequest
from chats.domain.chat_message.message_content import (
    ChatMessageContent,
    ChatMessageSubType,
    ProblemQuoteSource,
)
from chats.domain.chat_message.metadata import ChatMessageMetadata, SystemHint
from problems.domain.problem import GradeEnum, SubjectEnum


class AssistantMapper:
    @staticmethod
    def build_assistant_request(
        request_id: uuid.UUID,
        chat_id: int,
        subject: SubjectEnum,
        grade: GradeEnum,
        user_id: uuid.UUID,
        user_name: str,
        contents: list[ChatMessageContent],
        metadata: ChatMessageMetadata
    ) -> AssistantRequest:
        # 1. 준비
        user_query: str = ""
        prefix: str = ""
        user_images: list[str] = []
        problem_id: str | None = None

        for content in contents:
            if content.m_type == ChatMessageSubType.TEXT:
                user_query = content.value.text
            elif content.m_type == ChatMessageSubType.IMAGES:
                user_images = content.value.sources
            elif content.m_type == ChatMessageSubType.PROBLEM_LINK:
                problem_id = content.value.problem_id
            elif content.m_type == ChatMessageSubType.QUOTE:
                # 문제 or 채팅 중 일부 문구 인용이라면, user_query와 같이 넘겨줘야함
                prefix = content.value.text

                # 만약 PROBLEM 인용이면,
                if isinstance(content.value.source, ProblemQuoteSource):
                    # PROBLEM_LINK 와 같은 로직 탐
                    problem_id = content.value.source.problem_id

         # 문제의 인용 문구는 Prefix로 붙임
        if len(prefix) != 0:
            user_query = f"{prefix} {user_query}"


        system_hints = metadata.system_hints or []

        req = AssistantRequest(
            request_id=request_id,
            chat_id=chat_id,
            subject=subject,
            grade=grade,
            user_id=user_id,
            user_name=user_name,
            user_query=user_query,
            image_url=user_images,
            vector_problem_id=problem_id,
            translation_button=SystemHint.TRANSLATION_BUTTON in system_hints,
        )
        return req
