# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
from typing import AsyncGenerator, List, Optional
import uuid

import mlflow

from assistant.src.models.eng import EduQAEng
from assistant.src.models.math import EduQAMath
from assistant.src.schema import ModelParam, State, StudentProfile
from assistant_adapter.domain.assistant_state import AssistantState
from common.logger import logger
from config.config import service_config, env_config
from config.redis_cluster import get_sync_redis_client

mlflow.langchain.autolog()


class EduAssistant:
    """
    LLM(EduQA)에 질의하고 토큰을 AsyncGenerator로 반환하는 래퍼
    """

    def __init__(
        self,
        *,
        user_id: str,
        name: str,
        chat_id: int,
        grade: int,
        subject: str,
        loglevel: str = "INFO",
    ):
        self.chat_id = chat_id
        # 학습자 정보
        self._profile = StudentProfile(
            user_id=user_id,
            name=name,
            grade=grade,
        )

        # 모델 파라미터
        self._model_param = ModelParam(
            model=service_config.RESPONSE_MODEL,
            temperature=0.5,
        )

        # 과목별 모델 인스턴스
        self._model = (
            EduQAEng(
                self._profile,
                loglevel=loglevel,
                model_param=self._model_param,
                redis_client=get_sync_redis_client(),
            )
            if subject == "english"
            else EduQAMath(
                self._profile,
                loglevel=loglevel,
                model_param=self._model_param,
                redis_client=get_sync_redis_client(),
            )
        )

        self._state = State(messages=[])

    async def response(
        self,
        *,
        user_query: str,
        user_images: List[str],
        vector_problem_id: Optional[str] = None,
    ) -> AsyncGenerator[AssistantState, None]:
        """모델에게 사용자 질의를 전달하고, 응답을 토큰 단위로 yield

        :param user_query: 사용자 질의
        :param user_images: 유저가 전달한 이미지 목록 (현재는 최대 1개 전달)
        :param vector_problem_id: 모델에 이미지를 전달할 때 사용하는 vector DB의 problem_id 정보
        """
        # 사용자 메시지 구성
        content = [{"type": "text", "content": user_query}] + [
            {"type": "image", "content": url} for url in user_images
        ]

        # 모델에게 전달하기 전 준비 (prepare_for_model_request)
        self._state.messages.append({"role": "user", "content": content})
        self._state.db_problem_id = vector_problem_id
        # EduQA 모델 스트림 -> AssistantState 변환

        if mlflow.active_run() is not None:
            logger.error("MLFlow 이미 실행 중. 현재의 run 을 먼저 종료합니다.")
            mlflow.end_run()

        try:
            with mlflow.start_run(
                run_name=f"chat_id_{self.chat_id}_{uuid.uuid4().hex}", nested=False
            ) as run:
                mlflow.set_tag("chat_id", self.chat_id)
                async for raw_state in self._model.astream(
                    state=self._state, model_param=self._model_param
                ):
                    # 현재의 대화 내용을 기록합니다.
                    # 아직 완전한 대화 내용이 기록되진 않았지만, 기본 정보를 저장합니다.
                    state = AssistantState.from_raw(raw_state)
                    yield state
        except asyncio.CancelledError as e:
            logger.error(f"EduAssistant 가 캔슬되었습니다. : {e}")
        except Exception as e:
            logger.error(f"EduAssistant response failed: {e}")
            raise

        # 모델의 최종 State 값 갱신
        self._state = State(
            **self._model.graph.get_state(self._model.thread_config).values
        )

        # 최종 모델의 State도 내려줍니다.
        final_state = AssistantState.from_raw(self._state, final=True)

        yield final_state

    def save_long_term_memory(self):
        self._model.save_long_term_memory()
