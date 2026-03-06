# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import Depends

from goals.database.repository import GoalRepository
from goals.service.goal_service import GoalService


async def get_goal_repository(
) -> GoalRepository:
    return GoalRepository()


async def get_goal_service(
    goal_repository: GoalRepository = Depends(get_goal_repository)
) -> GoalService:
    return GoalService(
        goal_repository=goal_repository
    )
