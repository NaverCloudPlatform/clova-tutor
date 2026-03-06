# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any
from uuid import UUID

from chats.domain.chat import Chat
from chats.presentation.schemas.request_dto import ChatCreateRequestBody, ChatTitleUpdateRequestBody
from chats.presentation.schemas.response_dto import (
    ActiveGoalResponse,
    ChatDetailResponse,
    ChatResponse,
)
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import ChatAccessForbiddenException
from common.presentation.pagination import (
    CursorPaginateParams,
    CursorPaginateResponse,
    decode_cursor,
    encode_cursor,
)
from common.utils.utils import attach_timezone
from goals.domain.goal import Goal, GoalStatus
from goals.service.exceptions import NotFoundGoalException
from goals.service.goal_service import GoalService
from problems.domain.problem import GradeEnum, SubjectEnum


class ChatUseCase:
    def __init__(
        self,
        chat_service: ChatService,
        chat_problem_service: ChatProblemService,
        goal_service: GoalService,
    ):
        self.chat_service = chat_service
        self.chat_problem_service = chat_problem_service
        self.goal_service = goal_service


    async def _validate_chat(
        self,
        chat_id: int,
        user_id: UUID
    ) -> Chat:
        chat = await self.chat_service.get_chat_by_id(chat_id)
        if chat.user_id != user_id:
            raise ChatAccessForbiddenException(chat_id)
        return chat


    async def create_chat(
        self,
        req: ChatCreateRequestBody,
        user_id: UUID
    ) -> ChatResponse:
        new_chat = await self.chat_service.create_chat(
            title=req.title,
            user_id=user_id,
            subject=SubjectEnum(req.subject),
            grade=GradeEnum(int(req.grade))
        )

        return ChatResponse(
            **new_chat.model_dump(exclude={Chat.FIELD_LATEST_USED_AT}),
            has_problem=False,
            has_active_goal=False,
            latest_used_at=attach_timezone(new_chat.latest_used_at)
        )


    async def update_title(
        self,
        chat_id: int,
        req: ChatTitleUpdateRequestBody,
        user_id: UUID
    ) -> ChatResponse:
        """
        1. 채팅 제목 업데이트
        2. 문제 있는지 조사
        3. 활성화된 목표 있는지 조사
        """
        await self._validate_chat(
            chat_id=chat_id,
            user_id=user_id
        )
        # 1.
        chat = await self.chat_service.update_chat_title(chat_id,req.title)

        #2.
        has_problem = await self.chat_problem_service.exists_by_chat_id(chat_id)

        #3.
        has_active_goal = await self.goal_service.exists_by_chat_id(chat_id, status=GoalStatus.ACTIVE)

        return ChatResponse(
            **chat.model_dump(exclude={Chat.FIELD_LATEST_USED_AT}),
            has_problem=has_problem,
            has_active_goal=has_active_goal,
            latest_used_at=attach_timezone(chat.latest_used_at)
        )

    async def get_chat_detail(
        self,
        chat_id: int,
        user_id: UUID
    ) -> ChatDetailResponse:
        """
        1. 채팅 상세 정보 조회
        2. 채팅 목표 조회
        """

        # 1.
        chat = await self._validate_chat(chat_id, user_id)

        # 2.
        goal: Goal | None = None
        try:
            goal = await self.goal_service.get_goal_by_chat_id(chat_id=chat_id, status=GoalStatus.ACTIVE)
        except NotFoundGoalException:
            pass

        # 3.
        has_problem = await self.chat_problem_service.exists_by_chat_id(chat_id)

        active_goal: ActiveGoalResponse | None = None
        if goal:
            active_goal = ActiveGoalResponse(
                id=goal.id,
                goal_count=goal.goal_count,
                solved_count=goal.solved_count
            )

        return ChatDetailResponse(
            id=chat.id,
            title=chat.title,
            subject=chat.subject,
            has_problem=has_problem,
            has_active_goal= bool(goal is not None),
            active_goal=active_goal,
        )


    async def get_chat_list(
        self,
        user_id: UUID,
        subject: list[SubjectEnum] | None,
        paginate_filter: CursorPaginateParams
    ) -> CursorPaginateResponse[ChatResponse]:

        cursor_data: dict[str, Any] = {}
        if paginate_filter.cursor is not None:
            cursor_data = decode_cursor(paginate_filter.cursor)

        cursor_latest_used_at = cursor_data.get(Chat.FIELD_LATEST_USED_AT, None)
        cursor_id = cursor_data.get(Chat.FIELD_ID, None)

        chats = await self.chat_service.get_chat_list(
            user_id=user_id,
            subject_list=subject,
            size=paginate_filter.size,
            cursor_latest_used_at=cursor_latest_used_at,
            cursor_id=cursor_id
        )

        next_cursor: str | None = None
        if len(chats) == paginate_filter.size:
            last_chat = chats[-1]
            next_cursor = encode_cursor({
                Chat.FIELD_LATEST_USED_AT : last_chat.latest_used_at,
                Chat.FIELD_ID : last_chat.id
            })

        return CursorPaginateResponse(
            items=[
                ChatResponse(
                    id=chat.id,
                    title=chat.title,
                    subject=str(chat.subject),
                    has_problem=chat.has_problem,
                    has_active_goal=chat.has_active_goal,
                    latest_used_at=attach_timezone(chat.latest_used_at)
                )
                for chat in chats
            ],
            next_cursor=next_cursor
        )

    async def delete_chat(
        self,
        chat_id: int,
        user_id: UUID
    ) -> None:
        await self._validate_chat(
            chat_id=chat_id,
            user_id=user_id
        )

        await self.chat_service.delete_chat(chat_id)

        await self.chat_problem_service.delete_chat_problems_by_chat_id(
            chat_id=chat_id
        )
