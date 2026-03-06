# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from fastapi import APIRouter, Depends, status

from auths.dependencies import get_current_user_id

# from goals.dependencies import get_goal_usecase
from common.presentation.response import ErrorResponse
from goals.presentation.schemas.request_dto import GoalCreateRequestBody
from goals.presentation.schemas.response_dto import GoalResponse
from goals.usecase.goal_usecase import GoalUseCase

router = APIRouter()

@router.post(
    "",
    response_model=GoalResponse,
    description="채팅 방에 맞는 목표를 생성합니다."
)
async def create_goal(
    request: GoalCreateRequestBody,
    # 의존성 주입
    usecase: GoalUseCase = Depends(),
    user_id: UUID = Depends(get_current_user_id)
) -> GoalResponse:
    return (
        await usecase.create_active_goal(
            user_id=user_id,
            requset=request
        )
    )


@router.delete(
    "/{goal_id}",
    description="Active 한 목표를 Cancelled 로 바꿉니다.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "model": ErrorResponse,
            "description" : "목표 기록을 찾을 수 없습니다."
        }
    }
)
async def delete_goal(
    # path param
    goal_id: int,
    # dependency
    usecase: GoalUseCase = Depends(),
    user_id: UUID = Depends(get_current_user_id)
) -> None:
    return await usecase.cancel_goal(user_id, goal_id)
