# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from fastapi import Depends

from chats.dependencies import get_chat_service
from chats.service.chat_service import ChatService
from goals.dependencies import get_goal_service
from goals.domain.goal import GoalStatus
from goals.presentation.schemas.request_dto import GoalCreateRequestBody
from goals.presentation.schemas.response_dto import GoalResponse
from goals.service.exceptions import NotFoundGoalException
from goals.service.goal_service import GoalService
from goals.usecase.exceptions import ActiveGoalExistException


class GoalUseCase:
    def __init__(
        self,
        chat_service: ChatService = Depends(get_chat_service),
        goal_service: GoalService = Depends(get_goal_service)
    ):
        self.chat_service = chat_service
        self.goal_service = goal_service

    async def create_active_goal(
        self,
        user_id: UUID,
        requset: GoalCreateRequestBody
    ) -> GoalResponse:
        """"
        1. chat_id 조회
        2. 해당 채팅방 기존 Goal 있는지 조회
        3. 만약, Active Goal 있으면, 에러
        4. 그게 아니라면, 생성
        """

        # 1.
        chat = await self.chat_service.get_chat_by_id(chat_id=requset.chat_id)

        # 2.
        try:
            active_goal = await self.goal_service.get_goal_by_chat_id(chat.id, status=GoalStatus.ACTIVE)
            # 3.
            if active_goal:
                raise ActiveGoalExistException()
        except NotFoundGoalException:
            ...

        # 4.
        goal = await self.goal_service.create_goal(
            user_id=user_id,
            chat_id=chat.id,
            subject=chat.subject,
            goal_count=requset.goal_count
        )

        return GoalResponse(
            id=goal.id,
            goal_count=goal.goal_count,
            solved_count=goal.solved_count,
        )

    async def cancel_goal(
        self,
        user_id: UUID,
        goal_id: int
    ) -> None:
        """
        채팅방에서의 목표를 CANCELED 로 바꿉니다.(소프트 삭제, 하드 삭제는 하지 않습니다.)

        1. goal을 불러와 user_id가 맞는지 검증
        2. CANCELED 로 수정
        """

        # 1.
        goal = await self.goal_service.get_goal_by_id(goal_id)
        if user_id != goal.user_id:
            raise NotFoundGoalException(goal_id=goal.id)

        #2.
        await self.goal_service.change_goal_status(goal_id, GoalStatus.CANCELLED)


