# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from auths.dependencies import get_current_user_id
from chats.dependencies import get_problem_bookmark_usecase
from chats.domain.chat_problem import ProblemStatus
from chats.presentation.schemas.request_dto import ProblemBookmarkCreateRequestBody
from common.presentation.response import ErrorResponse
from chats.presentation.schemas.response_dto import (
    ProblemBookmarkCheckResponse,
    ProblemBookmarkCreateResponse,
    ProblemBookmarkResponse,
)
from chats.usecase.problem_bookmark_usecase import ProblemBookmarkUseCase
from common.presentation.pagination import CursorPaginateParams, CursorPaginateResponse
from problems.domain.problem import SubjectEnum

router = APIRouter()


@router.get(
    "",
    description="사용자가 등록한 문제 학습 노트 리스트 조회",
    response_model=CursorPaginateResponse[ProblemBookmarkResponse]
)
async def get_problem_bookmarks(
    # 쿼리 파라미터
    subject: SubjectEnum,
    status: list[ProblemStatus] = Query([]),
    cursor_param: CursorPaginateParams = Depends(),
    # 의존성
    usecase: ProblemBookmarkUseCase = Depends(get_problem_bookmark_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> CursorPaginateResponse[ProblemBookmarkResponse]:
    return await usecase.get_bookmark_list(
        user_id,
        subject,
        status_list=status,
        paginate_filter=cursor_param
    )

@router.get(
    "/problem/{problem_id}/check",
    description="현재 문제가 학습 노트에 이미 중복되어 저장되어 있는지 판단합니다.(chat_id와 무관)",
    response_model=ProblemBookmarkCheckResponse
)
async def check_problem_bookmark_duplicate(
    # Path 파라미터
    problem_id: str,
    # 의존성
    usecase: ProblemBookmarkUseCase = Depends(get_problem_bookmark_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ProblemBookmarkCheckResponse:
    return await usecase.check_problem_bookmark_duplicate(
        user_id,
        problem_id
    )

@router.patch(
    "",
    description="현재 채팅방의 문제를 북마크로 등록합니다.",
    response_model=ProblemBookmarkCreateResponse,
    responses={
        403: {"model": ErrorResponse, "description": "해당 채팅방에 대한 접근 권한이 없는 경우"},
        404: {"model": ErrorResponse, "description": "채팅방 또는 채팅 문제를 찾을 수 없는 경우"},
    },
)
async def bookmark_problem(
    # Body
    body: ProblemBookmarkCreateRequestBody,
    # 의존성
    usecase: ProblemBookmarkUseCase = Depends(get_problem_bookmark_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ProblemBookmarkCreateResponse:
    return await usecase.bookmark_problem(
        user_id=user_id,
        body=body
    )
