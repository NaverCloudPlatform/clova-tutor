# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import AsyncGenerator, cast

from langchain_naver import ChatClovaX

from assistant.src.schema.schema import ModelParam
from assistant.src.utils.load_utils import load_yaml
from assistant_adapter.domain.assistant_entry import AssistantEntry
from assistant_adapter.domain.assistant_state import AssistantState
from assistant_adapter.domain.edu_assistant import EduAssistant
from assistant_adapter.database.assistant_repository import AssistantRepository
from assistant_adapter.utils.constants import make_chat_title_prompt


class AssistantService:
    def __init__(
        self,
        repository: AssistantRepository,
    ) -> None:
        self.repo = repository

        api_info = load_yaml("assistant/api_info.yaml")
        MODEL_NAME = "hcx-005"
        model_param = ModelParam(
            temperature=0.5,
        )
        chatclovax_config = {
            **api_info[MODEL_NAME],
            **model_param.model_dump(exclude="model", exclude_none=True),
        }

        self.llm = ChatClovaX(**chatclovax_config, disable_streaming=True)

    async def get_or_create_assistant(
        self,
        user_id: str,
        chat_id: int,
        name: str,
        grade: int,
        subject: str,
    ) -> EduAssistant:
        entry = await self.repo.get(chat_id)
        if entry is None:
            entry = await self.repo.create(
                AssistantEntry(
                    EduAssistant(
                        user_id=user_id,
                        chat_id=chat_id,
                        name=name,
                        grade=grade,
                        subject=subject,
                    ),
                    repository=self.repo,
                )
            )
        entry.touch()
        return entry.assistant

    async def stream_response(
        self,
        assistant: EduAssistant,
        user_query: str,
        images: list[str],
        vector_problem_id: int,
    ) -> AsyncGenerator[AssistantState, None]:
        async for state in assistant.response(
            user_query=user_query,
            user_images=images,
            vector_problem_id=vector_problem_id,
        ):
            yield state

    async def create_chat_title(self, user_input: str) -> str:
        """
        사용자 입력을 받아 ChatClovaX 모델을 호출하고 결과를 문자열로 반환합니다.

        Args:
            user_input: 사용자 입력 문자열.

        Returns:
            모델의 응답 문자열.
        """

        # 1. user_input을 llm.invoke()에 전달
        response = await self.llm.ainvoke(make_chat_title_prompt(user_input))

        # 2. invoke의 결과가 LangChain의 BaseMessage나 유사한 객체일 경우,
        #    응답 내용을 문자열로 추출하여 반환
        if hasattr(response, "content"):
            return cast(str, response.content)
        else:
            # 응답이 이미 문자열인 경우
            return str(response)
