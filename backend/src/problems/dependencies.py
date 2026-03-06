# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import Depends

from problems.database.repository import ProblemRepository
from problems.service.problem_service import ProblemService
from problems.usecase.problem_usecase import ProblemUseCase


async def get_problem_repository() -> ProblemRepository:
    return ProblemRepository()

async def get_problem_service(
    repo: ProblemRepository = Depends(get_problem_repository)
) -> ProblemService:
    return ProblemService(repo)

async def get_problem_usecase(
    service: ProblemService = Depends(get_problem_service)
) -> ProblemUseCase:
    return ProblemUseCase(service)
