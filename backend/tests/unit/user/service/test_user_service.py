# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from users.database.models import UserModel
from users.database.repository.user_repo import UserFilter, UserRepository
from users.domain.user import User, UserWithDate
from users.service.exceptions import UserNotFoundException
from users.service.user_service import UserService


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    return AsyncMock(spec=UserRepository)

@pytest.fixture
def user_service(mock_user_repository: AsyncMock) -> UserService:
    return UserService(user_repo=mock_user_repository)


# -------------------------------------------------------
# get_user_list
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_user_list(
    user_service: UserService,
    mock_user_repository: AsyncMock,
):
    """
        1. 테스트 데이터 및 mock 반환값 준비
        2. get_user_list 메서드 호출
        3. 반환된 사용자 리스트 및 데이터 검증
    """

    # 1.
    TEST_USER_MODEL = UserModel(
        id=uuid.uuid4(),
        name="TEST",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_user_repository.get_list.return_value = [
        UserWithDate(
            **TEST_USER_MODEL.__dict__
        )
    ]

    # 2.
    users = await user_service.get_user_list()

    # 3.
    assert len(users) == 1
    assert users[0].id == TEST_USER_MODEL.id
    assert users[0].name == TEST_USER_MODEL.name
    assert users[0].grade == TEST_USER_MODEL.grade

    mock_user_repository.get_list.assert_called_once()


# -------------------------------------------------------
# get_user_by_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_user_by_id_success(
    user_service: UserService,
    mock_user_repository: AsyncMock,
):
    """
        1. get 호출 시 반환될 UserModel 설정
        2. get_user_by_id 메서드 호출
        3. 반환값 및 repository 호출 검증
    """

    # 1.
    TEST_USER_MODEL = UserModel(
        id=uuid.uuid4(),
        name="TEST",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_user_repository.get.return_value = TEST_USER_MODEL

    # 2.
    user = await user_service.get_user_by_id(TEST_USER_MODEL.id)

    # 3.
    assert isinstance(user, UserWithDate)
    assert user.id == TEST_USER_MODEL.id

    # get 메서드가 올바른 필터와 옵션으로 호출되었는지 확인
    mock_user_repository.get.assert_called_once()
    args, kwargs = mock_user_repository.get.call_args
    assert isinstance(args[0], UserFilter)
    assert args[0].id == TEST_USER_MODEL.id
    assert kwargs.get('convert_schema') is False


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    user_service: UserService,
    mock_user_repository: AsyncMock,
):
    """
        1. get 호출 시 None 반환 설정
        2. get_user_by_id 메서드 호출 및 UserNotFoundException 발생 확인
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    mock_user_repository.get.return_value = None

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_service.get_user_by_id(TEST_USER_ID)

    mock_user_repository.get.assert_called_once()

# -------------------------------------------------------
# create_user
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_user(
    user_service: UserService,
    mock_user_repository: AsyncMock,
):
    """
        1. 생성용 입력값 및 mock 반환값 준비
        2. create_user 메서드 호출
        3. 생성된 사용자 및 repository 호출 검증
    """

    # 1.
    NEW_NAME = "TESTUSER"
    NEW_GRADE = 5
    NEW_MEMO = "TEST MEMO"
    TEST_USER_MODEL = User(
        id=uuid.uuid4(),
        name=NEW_NAME,
        grade=NEW_GRADE,
        memo=NEW_MEMO
    )
    mock_user_repository.create.return_value = TEST_USER_MODEL

    # 2.
    created_user = await user_service.create_user(
        name=NEW_NAME, grade=NEW_GRADE, memo=NEW_MEMO
    )

    #
    assert created_user.name == NEW_NAME
    assert created_user.grade == NEW_GRADE
    assert created_user.memo == NEW_MEMO
    assert isinstance(created_user.id, uuid.UUID)

    # create 메서드가 올바른 인자(User 객체)로 호출되었는지 확인
    mock_user_repository.create.assert_called_once()

    # 호출된 인스턴스의 타입과 속성 확인
    called_user_obj = mock_user_repository.create.call_args[0][0]
    assert isinstance(called_user_obj, User)
    assert called_user_obj.name == NEW_NAME
    assert called_user_obj.grade == NEW_GRADE


# -------------------------------------------------------
# update_user
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_update_user_success(
    user_service: UserService,
    mock_user_repository: AsyncMock,
):
    """
        1. 기존 사용자 조회 및 업데이트 결과 mock 설정
        2. update_from_model 호출 시 업데이트된 UserWithDate 반환
        3. update_user 메서드 호출
        4. 업데이트 결과 및 호출 여부 검증
    """

    # 1.
    TEST_USER_MODEL = UserModel(
        id=str(uuid.uuid4()),
        name="TEST",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_user_repository.get.return_value = TEST_USER_MODEL

    # 2.
    UPDATED_DATA = {"name": "UPDATED_NAME", "grade": 3}
    updated_model = UserWithDate(
        id=TEST_USER_MODEL.id,
        name=UPDATED_DATA["name"],
        grade=UPDATED_DATA["grade"],
        memo=TEST_USER_MODEL.memo,
        created_at=TEST_USER_MODEL.created_at,
        updated_at=datetime.now()
    )
    mock_user_repository.update_from_model.return_value = updated_model

    # 3.
    updated_user = await user_service.update_user(
        TEST_USER_MODEL.id,
        UPDATED_DATA
    )

    # 4.
    assert updated_user.name == UPDATED_DATA["name"]
    assert updated_user.grade == UPDATED_DATA["grade"]
    assert isinstance(updated_user, UserWithDate)

    # get 호출 확인
    mock_user_repository.get.assert_called_once()

    # update_from_model 호출 확인
    mock_user_repository.update_from_model.assert_called_once_with(
        TEST_USER_MODEL,
        update=UPDATED_DATA,
    )


@pytest.mark.asyncio
async def test_update_user_not_found(
    user_service: UserService,
    mock_user_repository: AsyncMock,
):
    """
        1. get 호출 시 None 반환 설정
        2. update_user 메서드 호출 및 UserNotFoundException 발생 확인
    """

    # 1.
    mock_user_repository.get.return_value = None

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_service.update_user(uuid.uuid4(), {"name": "fail"})

    mock_user_repository.get.assert_called_once()
    # 사용자를 찾지 못했으므로 update_from_model은 호출되지 않아야 함
    mock_user_repository.update_from_model.assert_not_called()


# -------------------------------------------------------
# delete_user
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_user(
    user_service: UserService,
    mock_user_repository: AsyncMock,
):
    """
        1. delete 호출 mock 설정
        2. delete_user 메서드 호출
        3. delete 호출 인자 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    mock_user_repository.delete.return_value = None

    # 2.
    await user_service.delete_user(TEST_USER_ID)

    # 3.
    mock_user_repository.delete.assert_called_once()
    args, _ = mock_user_repository.delete.call_args
    assert isinstance(args[0], UserFilter)
    assert args[0].id == TEST_USER_ID
