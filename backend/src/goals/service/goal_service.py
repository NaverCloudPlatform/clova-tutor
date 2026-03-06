# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from typing import Any
from uuid import UUID

from goals.database.repository import GoalFilter, GoalRepository
from goals.domain.goal import Goal, GoalStatus
from goals.service.exceptions import InvalidGoalValueExeception, NotFoundGoalException
from problems.domain.problem import SubjectEnum


class GoalService:
    def __init__(
        self,
        goal_repository: GoalRepository
    ):
        self.goal_repository = goal_repository


    async def exists_by_chat_id(
        self,
        chat_id: int,
        *,
        status: GoalStatus | None = None
    ) -> bool:
        return (await self.goal_repository.exists(flt=GoalFilter(chat_id=chat_id, status=status)))

    async def create_goal(
        self,
        user_id: UUID,
        chat_id: int,
        subject: SubjectEnum,
        goal_count: int,
        solved_count: int = 0,
        status: GoalStatus = GoalStatus.ACTIVE
    ) -> Goal:
        new_goal = Goal(
            user_id=user_id,
            chat_id=chat_id,
            subject=subject,
            goal_count=goal_count,
            solved_count=solved_count,
            status=status,
            finished_at=None
        )

        created_goal: Goal = await self.goal_repository.create(new_goal)
        return created_goal


    async def get_goal_by_id(self,goal_id: int, *, status: GoalStatus | None = None) -> Goal:
        goal: Goal | None = await self.goal_repository.get(flt=GoalFilter(
            id=goal_id,
            status=status
            )
        )
        if goal is None:
            raise NotFoundGoalException(goal_id)

        return goal


    async def get_goal_by_chat_id(self, chat_id: int, *, status: GoalStatus | None = None
    ) -> Goal:
        goal: Goal | None = await self.goal_repository.get(flt=GoalFilter(
            chat_id=chat_id,
            status=status
            )
        )
        if goal is None:
            raise NotFoundGoalException()
        return goal

    async def list_goal_by_chat_id(
        self,
        chat_id: int,
        *,
        status: GoalStatus | None = None
    ) -> list[Goal]:
        goal_list: list[Goal] = await self.goal_repository.get_list(flt=GoalFilter(chat_id=chat_id, status=status))
        return goal_list


    async def change_goal_status(self, goal_id: int, goal_status: GoalStatus) -> Goal:
        goal_for_update= await self.goal_repository.get(
            flt=GoalFilter(id=goal_id),
            convert_schema=False
        )
        if goal_for_update is None:
            raise NotFoundGoalException(goal_id)

        # 만약 상태가 같다면, 아무것도 하지 않음
        if goal_for_update.status == goal_status:
            return self.goal_repository._convert(goal_for_update, convert_schema=None)

        goal_for_update.status = goal_status
        updated_goal = await self.goal_repository.update_from_model(
            goal_for_update,
            update= {
                Goal.FIELD_STATUS:  goal_status,
            }
        )
        return updated_goal


    async def update_solved_count(self, goal_id: int, delta_solved_count: int = 1) -> Goal:
        """
        solved_count 를 변화시킬 때 쓰는 서비스입니다.

        정합성 테스트를 진행하여 목표치와 같아진 경우에는 완료를 갱신합니다.
        """
        goal_for_update = await self.goal_repository.get(
            flt=GoalFilter(id=goal_id),
            convert_schema=False
        )
        if goal_for_update is None:
            raise NotFoundGoalException(goal_id)

        new_count = goal_for_update.solved_count + delta_solved_count

        update_dict: dict[str, Any] = {
            Goal.FIELD_SOLVED_COUNT: new_count,
        }
        # case 1. 0 보다 작아질 경우
        if new_count < 0:
            raise InvalidGoalValueExeception("solved_count는 0보다 작을 수 없습니다.")

        # case 2. 목표 달성보다 클 경우
        if new_count > goal_for_update.goal_count:
            raise InvalidGoalValueExeception("solved_count는 목표치를 초과할 수 없습니다.")

        # case 3. 목표 달성 시
        if new_count == goal_for_update.goal_count:
            update_dict.update({
                Goal.FIELD_STATUS: GoalStatus.COMPLETED,
                Goal.FIELD_FINISHED_AT: datetime.now()
            })

        updated_goal = await self.goal_repository.update_from_model(
            goal_for_update,
            update=update_dict
        )
        return updated_goal
