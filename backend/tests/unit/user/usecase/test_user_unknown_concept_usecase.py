# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from users.domain.user import UserWithDate
from users.domain.user_unknown_concept import UserUnknownConcept, UserUnknownConceptWithDate
from users.presentation.schemas.request_dto import UnknownConceptCreateRequestBody
from users.presentation.schemas.response_dto import UnknownConceptResponse
from users.service.exceptions import UserNotFoundException, UserUnknownConceptNotFoundException
from users.service.user_service import UserService
from users.service.user_unknown_concept_service import UserUnknownConceptService
from users.usecase.user_unknown_concept_usecase import UserUnknownConceptUseCase


@pytest.fixture
def mock_user_service() -> AsyncMock:
    return AsyncMock(spec=UserService)


@pytest.fixture
def mock_unknown_concept_service() -> AsyncMock:
    return AsyncMock(spec=UserUnknownConceptService)


@pytest.fixture
def user_unknown_concept_use_case(
    mock_user_service: AsyncMock,
    mock_unknown_concept_service: AsyncMock,
) -> UserUnknownConceptUseCase:
    return UserUnknownConceptUseCase(
        user_service=mock_user_service,
        unknown_concept_service=mock_unknown_concept_service,
    )


# -------------------------------------------------------
# _validate_user
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_validate_user_success(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. get_user_by_id가 UserWithDate를 반환하도록 설정
        2. _validate_user 호출
        3. 반환된 사용자 및 호출 검증
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
    user = await user_unknown_concept_use_case._validate_user(TEST_USER_ID)

    # 3.
    assert user.id == TEST_USER_ID
    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)


@pytest.mark.asyncio
async def test_validate_user_not_found(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_user_service: AsyncMock,
):
    """
        1. get_user_by_id가 None 반환하도록 설정
        2. _validate_user 호출
        3. UserNotFoundException 발생 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    mock_user_service.get_user_by_id.return_value = None

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_unknown_concept_use_case._validate_user(TEST_USER_ID)

    # 3.
    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)


# -------------------------------------------------------
# list_unknown_concepts
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_list_unknown_concepts_with_subject_filter(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_user_service: AsyncMock,
    mock_unknown_concept_service: AsyncMock,
):
    """
        1. 사용자 유효성 검사 성공 및 개념 목록 반환 설정
        2. list_unknown_concepts 호출
        3. 응답 타입 및 호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_SUBJECT = "과학"

    TEST_USER = UserWithDate(
        id=TEST_USER_ID,
        name="테스트 사용자",
        grade=1,
        memo=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    TEST_CONCEPT = UserUnknownConceptWithDate(
        id=1,
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
        key_concept="중력",
        unknown_concept="자유 낙하",
        unknown_concept_reason="이해 안 됨",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_user_service.get_user_by_id.return_value = TEST_USER
    mock_unknown_concept_service.list_concepts_by_user_id.return_value = [TEST_CONCEPT]

    # 2.
    results = await user_unknown_concept_use_case.list_unknown_concepts(
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
    )

    # 3.
    assert len(results) == 1
    assert isinstance(results[0], UnknownConceptResponse)

    mock_user_service.get_user_by_id.assert_called_once_with(TEST_USER_ID)
    mock_unknown_concept_service.list_concepts_by_user_id.assert_called_once_with(
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
    )


@pytest.mark.asyncio
async def test_list_unknown_concepts_user_not_found(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_user_service: AsyncMock,
    mock_unknown_concept_service: AsyncMock,
):
    """
        1. 사용자 유효성 검사 실패 설정
        2. list_unknown_concepts 호출
        3. UserNotFoundException 및 서비스 미호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    mock_user_service.get_user_by_id.return_value = None

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_unknown_concept_use_case.list_unknown_concepts(
            user_id=TEST_USER_ID,
            subject=None,
        )

    # 3.
    mock_unknown_concept_service.list_concepts_by_user_id.assert_not_called()


# -------------------------------------------------------
# upsert_concept
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_concept_create(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_user_service: AsyncMock,
    mock_unknown_concept_service: AsyncMock,
):
    """
        1. 기존 개념 조회 시 NotFound 예외 발생 설정
        2. create_user_unknown_concept 반환 설정
        3. upsert_concept 호출 및 create 경로 검증
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

    REQUEST_BODY = UnknownConceptCreateRequestBody(
        subject="수학",
        key_concept="삼각함수",
        unknown_concept="사인 법칙",
        unknown_concept_reason="어려움",
    )

    CREATED_CONCEPT = UserUnknownConceptWithDate(
        id=10,
        user_id=TEST_USER_ID,
        **REQUEST_BODY.model_dump(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_user_service.get_user_by_id.return_value = TEST_USER
    mock_unknown_concept_service.get_concepts_by_user_id_and_subject_and_key_concept.side_effect = (
        UserUnknownConceptNotFoundException
    )
    mock_unknown_concept_service.create_user_unknown_concept.return_value = CREATED_CONCEPT

    # 2.
    result = await user_unknown_concept_use_case.upsert_concept(
        user_id=TEST_USER_ID,
        body=REQUEST_BODY,
    )

    # 3.
    assert isinstance(result, UnknownConceptResponse)

    mock_unknown_concept_service.get_concepts_by_user_id_and_subject_and_key_concept.assert_called_once()
    mock_unknown_concept_service.create_user_unknown_concept.assert_called_once()
    mock_unknown_concept_service.update_user_unknown_concept_and_reason_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_concept_update(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_user_service: AsyncMock,
    mock_unknown_concept_service: AsyncMock,
):
    """
        1. 기존 개념 존재 설정
        2. update_user_unknown_concept_and_reason_by_id 반환 설정
        3. upsert_concept 호출 및 update 경로 검증
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

    EXISTING_CONCEPT = UserUnknownConcept(
        id=5,
        user_id=TEST_USER_ID,
        subject="과학",
        key_concept="중력",
        unknown_concept="이전 개념",
        unknown_concept_reason="이전 사유",
    )

    REQUEST_BODY = UnknownConceptCreateRequestBody(
        subject="과학",
        key_concept="중력",
        unknown_concept="새 개념",
        unknown_concept_reason="이제 이해함",
    )

    UPDATED_CONCEPT = UserUnknownConceptWithDate(
        id=5,
        user_id=TEST_USER_ID,
        **REQUEST_BODY.model_dump(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_user_service.get_user_by_id.return_value = TEST_USER
    mock_unknown_concept_service.get_concepts_by_user_id_and_subject_and_key_concept.return_value = EXISTING_CONCEPT
    mock_unknown_concept_service.update_user_unknown_concept_and_reason_by_id.return_value = UPDATED_CONCEPT

    # 2.
    result = await user_unknown_concept_use_case.upsert_concept(
        user_id=TEST_USER_ID,
        body=REQUEST_BODY,
    )

    # 3.
    assert isinstance(result, UnknownConceptResponse)
    assert result.id == UPDATED_CONCEPT.id

    mock_unknown_concept_service.update_user_unknown_concept_and_reason_by_id.assert_called_once_with(
        id=EXISTING_CONCEPT.id,
        unknown_concept=REQUEST_BODY.unknown_concept,
        unknown_concept_reason=REQUEST_BODY.unknown_concept_reason,
    )
    mock_unknown_concept_service.create_user_unknown_concept.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_concept_user_not_found(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_user_service: AsyncMock,
    mock_unknown_concept_service: AsyncMock,
):
    """
        1. 사용자 유효성 검사 실패 설정
        2. upsert_concept 호출
        3. UserNotFoundException 및 서비스 미호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    REQUEST_BODY = UnknownConceptCreateRequestBody(
        subject="과학",
        key_concept="중력",
        unknown_concept="실험",
        unknown_concept_reason="모름",
    )
    mock_user_service.get_user_by_id.return_value = None

    # 2.
    with pytest.raises(UserNotFoundException):
        await user_unknown_concept_use_case.upsert_concept(
            user_id=TEST_USER_ID,
            body=REQUEST_BODY,
        )

    # 3.
    mock_unknown_concept_service.get_concepts_by_user_id_and_subject_and_key_concept.assert_not_called()


# -------------------------------------------------------
# delete_concept
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_concept_with_all_filters(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_unknown_concept_service: AsyncMock,
):
    """
        1. 모든 필터를 포함하여 delete_concept 호출
        2. delete_by_user_id 호출 인자 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_SUBJECT = "영어"
    TEST_KEY_CONCEPT = "시제"

    # 2.
    await user_unknown_concept_use_case.delete_concept(
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
        key_concept=TEST_KEY_CONCEPT,
    )

    # 3.
    mock_unknown_concept_service.delete_by_user_id.assert_called_once_with(
        TEST_USER_ID,
        subject=TEST_SUBJECT,
        key_concept=TEST_KEY_CONCEPT,
    )


@pytest.mark.asyncio
async def test_delete_concept_only_user_id(
    user_unknown_concept_use_case: UserUnknownConceptUseCase,
    mock_unknown_concept_service: AsyncMock,
):
    """
        1. user_id만으로 delete_concept 호출
        2. delete_by_user_id 전체 삭제 호출 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()

    # 2.
    await user_unknown_concept_use_case.delete_concept(
        user_id=TEST_USER_ID,
        subject=None,
        key_concept=None,
    )

    # 3.
    mock_unknown_concept_service.delete_by_user_id.assert_called_once_with(
        TEST_USER_ID,
        subject=None,
        key_concept=None,
    )
