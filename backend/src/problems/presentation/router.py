# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import APIRouter, Depends

from common.presentation.auth_internal_api import verify_internal_api_key
from common.presentation.response import ErrorResponse
from problems.dependencies import get_problem_usecase
from problems.presentation.schemas.request_dto import ProblemCreateRequestBody
from problems.presentation.schemas.response_dto import ProblemCreateResponse, ProblemResponse
from problems.usecase.problem_usecase import ProblemUseCase

router = APIRouter()

@router.get(
    "/{problem_id}",
    response_model=ProblemResponse,
    description="problem_id에 해당하는 문제 정보를 반환합니다.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "해당 문제가 존재하지 않을 경우 반환됩니다.",
        },
    },
)
async def get_problem(
    # Path 파라미터
    problem_id: str,
    # 의존성
    usecase: ProblemUseCase = Depends(get_problem_usecase)
) -> ProblemResponse:
    problem = await usecase.get_problem(problem_id)
    return problem


@router.post(
    "",
    description="문제 생성 API 입니다.",
    dependencies=[Depends(verify_internal_api_key)]
)
async def create_problems(
    # Body
    body: ProblemCreateRequestBody,
    # 의존성
    usecase: ProblemUseCase = Depends(get_problem_usecase)
) -> ProblemCreateResponse:
    problem_ids = await usecase.create_bulk_problems(body)
    return problem_ids

