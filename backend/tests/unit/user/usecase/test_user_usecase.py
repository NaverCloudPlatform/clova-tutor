# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from users.domain.user import User, UserWithDate
from users.presentation.schemas.request_dto import UserCreateRequestBody, UserUpdateRequestBody
from users.presentation.schemas.response_dto import (
    UserCreateResponse,
    UserResponse,
    UserUpdateResponse,
)
from users.service.exceptions import UserNotFoundException
from users.service.user_service import UserService
from users.usecase.user_usecase import UserUseCase


@pytest.fixture
def mock_user_service() -> AsyncMock:
    return AsyncMock(spec=UserService)

@pytest.fixture
def user_use_case(mock_user_service: AsyncMock) -> UserUseCase:
    return UserUseCase(user_service=mock_user_service)


# -------------------------------------------------------
# _validate_user_id
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_validate_user_id_success(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. get_user_by_id가 정상 UserWithDate를 반환하도록 설정
        2. _validate_user_id 호출
        3. 예외 없이 통과 및 호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_USER = UserWithDate(
        id=TEST_USER_ID,
        name="테스트 사용자",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_user_service.get_user_by_id.return_value = TEST_USER

    # 2.
    await user_use_case._validate_user_id(TEST_USER_ID)

    # 3.
    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)


@pytest.mark.asyncio
async def test_validate_user_id_not_found(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. get_user_by_id가 None 반환하도록 설정
        2. _validate_user_id 호출
        3. UserNotFoundException 발생 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    mock_user_service.get_user_by_id.return_value = None

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_use_case._validate_user_id(TEST_USER_ID)

    # 3.
    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)


# -------------------------------------------------------
# get_users
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_users(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. UserService.get_user_list 반환값 설정
        2. get_users 호출
        3. UserResponse 매핑 및 타임존 검증
    """

    # 1.
    TEST_USER = UserWithDate(
        id=uuid.uuid4(),
        name="테스트 사용자",
        grade=1,
        memo="메모",
        created_at=datetime.now() - timedelta(days=1),
        updated_at=datetime.now(),
    )
    mock_user_service.get_user_list.return_value = [TEST_USER]

    # 2.
    users = await user_use_case.get_users()

    # 3.
    assert len(users) == 1
    assert isinstance(users[0], UserResponse)
    assert users[0].id == TEST_USER.id
    assert users[0].created_at.tzinfo is not None

    mock_user_service.get_user_list.assert_called_once()


# -------------------------------------------------------
# get_user_by_id
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_user_by_id_success(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. get_user_by_id 반환 UserWithDate 설정
        2. get_user_by_id 호출
        3. UserResponse 변환 및 호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_USER = UserWithDate(
        id=TEST_USER_ID,
        name="테스트",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_user_service.get_user_by_id.return_value = TEST_USER

    # 2.
    response = await user_use_case.get_user_by_id(TEST_USER_ID)

    # 3.
    assert isinstance(response, UserResponse)
    assert response.id == TEST_USER_ID
    assert response.created_at.tzinfo is not None

    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)


# -------------------------------------------------------
# create_user
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_create_user(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. 생성 요청 Body 및 User 도메인 설정
        2. create_user 호출
        3. 생성 결과 및 호출 인자 검증
    """

    # 1.
    TEST_USER = User(
        id=uuid.uuid4(),
        name="새 사용자",
        grade=5,
        memo=None,
    )
    REQUEST_BODY = UserCreateRequestBody(
        name=TEST_USER.name,
        grade=TEST_USER.grade,
        memo=TEST_USER.memo,
    )
    mock_user_service.create_user.return_value = TEST_USER

    # 2.
    response = await user_use_case.create_user(body=REQUEST_BODY)

    # 3.
    assert isinstance(response, UserCreateResponse)
    assert response.id == TEST_USER.id
    assert response.name == TEST_USER.name

    mock_user_service.create_user.assert_called_once_with(
        name=REQUEST_BODY.name,
        grade=REQUEST_BODY.grade,
        memo=REQUEST_BODY.memo,
    )


# -------------------------------------------------------
# patch_user
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_patch_user_success(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. 기존 사용자 조회 및 업데이트 결과 설정
        2. patch_user 호출
        3. 업데이트 결과 및 내부 호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    ORIGINAL_USER = UserWithDate(
        id=TEST_USER_ID,
        name="기존 이름",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    UPDATED_NAME = "새 이름"

    UPDATED_USER = UserWithDate(
        **ORIGINAL_USER.model_dump(exclude={"name", "updated_at"}),
        name=UPDATED_NAME,
        updated_at=datetime.now(),
    )

    mock_user_service.get_user_by_id.return_value = ORIGINAL_USER
    mock_user_service.update_user.return_value = UPDATED_USER

    REQUEST_BODY = UserUpdateRequestBody(name=UPDATED_NAME)
    UPDATE_DICT = REQUEST_BODY.model_dump(exclude_unset=True)

    # 2.
    response = await user_use_case.patch_user(
        user_id=TEST_USER_ID,
        body=REQUEST_BODY,
    )

    # 3.
    assert isinstance(response, UserUpdateResponse)
    assert response.name == UPDATED_NAME

    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)
    mock_user_service.update_user.assert_called_once_with(
        TEST_USER_ID,
        update_dict=UPDATE_DICT,
    )


@pytest.mark.asyncio
async def test_patch_user_not_found(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. get_user_by_id가 None 반환하도록 설정
        2. patch_user 호출
        3. UserNotFoundException 발생 및 update 미호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    mock_user_service.get_user_by_id.return_value = None
    REQUEST_BODY = UserUpdateRequestBody(name="fail")

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_use_case.patch_user(
            user_id=TEST_USER_ID,
            body=REQUEST_BODY,
        )

    # 3.
    mock_user_service.update_user.assert_not_called()


# -------------------------------------------------------
# delete_user
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_user_success(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. 기존 사용자 존재 가정
        2. delete_user 호출
        3. 내부 호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_USER = UserWithDate(
        id=TEST_USER_ID,
        name="삭제 대상",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_user_service.get_user_by_id.return_value = TEST_USER
    mock_user_service.delete_user.return_value = None

    # 2.
    await user_use_case.delete_user(user_id=TEST_USER_ID)

    # 3.
    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)
    mock_user_service.delete_user.assert_called_once_with(TEST_USER_ID)


@pytest.mark.asyncio
async def test_delete_user_not_found(
    user_use_case: UserUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. get_user_by_id가 None 반환하도록 설정
        2. delete_user 호출
        3. UserNotFoundException 발생 및 delete 미호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    mock_user_service.get_user_by_id.return_value = None

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_use_case.delete_user(user_id=TEST_USER_ID)

    # 3.
    mock_user_service.delete_user.assert_not_called()
