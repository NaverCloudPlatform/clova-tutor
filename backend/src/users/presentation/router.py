# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from common.presentation.response import ErrorResponse
from users.dependencies import get_user_unknown_concept_usecase, get_user_usecase
from users.presentation.schemas.request_dto import (
    UnknownConceptCreateRequestBody,
    UserCreateRequestBody,
    UserUpdateRequestBody,
)
from users.presentation.schemas.response_dto import (
    UnknownConceptResponse,
    UserCreateResponse,
    UserResponse,
    UserUpdateResponse,
)
from users.usecase.user_unknown_concept_usecase import UserUnknownConceptUseCase
from users.usecase.user_usecase import UserUseCase

router = APIRouter()


@router.get(
    "", response_model=list[UserResponse], description="전체 사용자 목록 조회"
)
async def get_users(
    # 의존성
    usecase: UserUseCase = Depends(get_user_usecase),
) -> list[UserResponse]:
    """모든 사용자 목록을 조회합니다.

    Args:
        service (UserService): 사용자 서비스 객체

    Returns:
        List[UserResponse]: 사용자 목록
    """
    return await usecase.get_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    description="특정 사용자 정보 조회",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "사용자를 찾을 수 없는 경우",
        },
    },
)
async def get_user(
    # Path 파라미터
    user_id: UUID,
    # 의존성
    usecase: UserUseCase = Depends(get_user_usecase),
) -> UserResponse:
    """특정 사용자의 정보를 조회합니다.

    Args:
        service (UserDetailService): 사용자 상세 서비스 객체

    Returns:
        UserResponse: 조회된 사용자 정보

    Raises:
        UserNotFoundException: 사용자를 찾을 수 없는 경우
    """
    return await usecase.get_user_by_id(user_id)


@router.post(
    "",
    response_model=UserCreateResponse,
    description="신규 사용자 생성",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    # Body
    body: UserCreateRequestBody,
    # 의존성
    usecase: UserUseCase = Depends(get_user_usecase),
) -> UserCreateResponse:
    """새로운 사용자를 생성합니다.

    Args:
        user (UserCreateRequest): 사용자 생성 요청 데이터
        service (UserService): 사용자 서비스 객체

    Returns:
        UserResponse: 생성된 사용자 정보
    """
    return await usecase.create_user(body)


@router.patch(
    "/{user_id}",
    response_model=UserUpdateResponse,
    description="유저 정보를 수정합니다.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "사용자를 찾을 수 없는 경우",
        },
    }
)
async def patch_user(
    # Path 파라미터
    user_id: UUID,
    # Body
    body: UserUpdateRequestBody,
    # 의존성
    usecase: UserUseCase = Depends(get_user_usecase),
) -> UserUpdateResponse:
    return await usecase.patch_user(user_id, body)


@router.delete(
    "/{user_id}",
    description="특정 사용자 삭제",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "사용자를 찾을 수 없는 경우",
        },
    },
)
async def delete_user(
    # Path 파라미터
    user_id: UUID,
    # 의존성
    usecase: UserUseCase = Depends(get_user_usecase),
) -> Response:
    """특정 사용자를 삭제합니다.

    Args:
        service (UserDetailService): 사용자 상세 서비스 객체

    Raises:
        UserNotFoundException: 사용자를 찾을 수 없는 경우
    """
    await usecase.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)




@router.get(
    "/{user_id}/unknown-concepts",
    description="사용자의 이해하지 못한 개념 목록 조회",
    response_model=list[UnknownConceptResponse],
)
async def get_unknown_concepts_list(
    # Path 파라미터
    user_id: UUID,
    # 쿼리 파라미터
    subject: str | None = Query(None),
    # 의존성
    usecase: UserUnknownConceptUseCase = Depends(get_user_unknown_concept_usecase),
) -> list[UnknownConceptResponse]:
    """사용자가 이해하지 못한 개념 목록을 조회합니다.

    Args:
        subject (Optional[str], optional): 과목명으로 필터링. Defaults to None
        service (UserUnknownConceptService): 이해하지 못한 개념 서비스 객체

    Returns:
        List[UnknownConceptReadResponse]: 이해하지 못한 개념 목록
    """
    return  await usecase.list_unknown_concepts(user_id, subject)



@router.put(
    "/{user_id}/unknown-concepts",
    description="사용자의 이해하지 못한 개념 생성 또는 갱신",
    response_model=UnknownConceptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upsert_unknown_concept(
    # Path 파라미터
    user_id: UUID,
    # Body
    body: UnknownConceptCreateRequestBody,
    # 의존성
    usecase: UserUnknownConceptUseCase = Depends(get_user_unknown_concept_usecase),
) -> UnknownConceptResponse:
    """사용자의 이해하지 못한 개념을 생성하거나 갱신합니다.

    Args:
        unknown_concept (UnknownConceptCreateRequest): 이해하지 못한 개념 생성/갱신 요청 데이터
        service (UserUnknownConceptService): 이해하지 못한 개념 서비스 객체

    Returns:
        UnknownConceptReadResponse: 생성/갱신된 이해하지 못한 개념 정보
    """
    response = await usecase.upsert_concept(user_id, body)
    return response


@router.delete(
    "/{user_id}/unknown-concepts",
    description="사용자의 이해하지 못한 개념 삭제",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_unknown_concept(
    # Path 파라미터
    user_id: UUID,
    # 쿼리 파라미터
    subject: str | None = Query(None),
    key_concept: str | None = Query(None),
    # 의존성
    usecase: UserUnknownConceptUseCase = Depends(get_user_unknown_concept_usecase),
) -> Response:
    """사용자의 이해하지 못한 개념을 삭제합니다.

    Args:
        subject (str, optional): 과목명으로 필터링. Defaults to None
        key_concept (str, optional): 주요 개념으로 필터링. Defaults to None
        service (UserUnknownConceptService): 이해하지 못한 개념 서비스 객체
    """
    await usecase.delete_concept(user_id, subject, key_concept)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
