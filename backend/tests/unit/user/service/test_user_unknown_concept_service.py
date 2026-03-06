# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


import uuid

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from users.database.models import UserUnknownConceptModel
from users.database.repository.unknown_concept_repo import (
    UserUnknownConceptFilter,
    UserUnknownConceptRepository,
)
from users.domain.user_unknown_concept import UserUnknownConcept, UserUnknownConceptWithDate
from users.service.exceptions import UserUnknownConceptNotFoundException
from users.service.user_unknown_concept_service import UserUnknownConceptService


@pytest.fixture
def mock_user_unknown_repository() -> AsyncMock:
    return AsyncMock(spec=UserUnknownConceptRepository)

@pytest.fixture
def user_unknown_concept_service(mock_user_unknown_repository: AsyncMock) -> UserUnknownConceptService:
    return UserUnknownConceptService(unknown_concept_repo=mock_user_unknown_repository)


# -------------------------------------------------------
# get_concepts_by_user_id_and_subject_and_key_concept
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_get_concept_success(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. 테스트 데이터 및 mock 반환값 준비
        2. service 메서드 호출
        3. 반환값 및 filter 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CONCEPT = UserUnknownConcept(
        id=1,
        user_id=TEST_USER_ID,
        subject="수학",
        key_concept="삼각함수",
        unknown_concept="사인 법칙",
        unknown_concept_reason="개념이 어려움",
    )
    mock_user_unknown_repository.get.return_value = TEST_CONCEPT

    # 2.
    result = await user_unknown_concept_service.get_concepts_by_user_id_and_subject_and_key_concept(
        user_id=TEST_USER_ID,
        subject="수학",
        key_concept="삼각함수",
    )

    # 3.
    assert result.id == TEST_CONCEPT.id
    mock_user_unknown_repository.get.assert_called_once()

    _, kwargs = mock_user_unknown_repository.get.call_args
    flt = kwargs['flt']
    assert isinstance(flt, UserUnknownConceptFilter)
    assert flt.user_id == TEST_CONCEPT.user_id
    assert flt.subject == TEST_CONCEPT.subject
    assert flt.key_concept == TEST_CONCEPT.key_concept


@pytest.mark.asyncio
async def test_get_concept_not_found(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. repository.get None 반환 설정
        2. service 메서드 호출 및 NotFoundException 발생 검증
    """
    # 1.
    mock_user_unknown_repository.get.return_value = None

    # 2.
    with pytest.raises(UserUnknownConceptNotFoundException):
        await user_unknown_concept_service.get_concepts_by_user_id_and_subject_and_key_concept(
            user_id=uuid.uuid4(),
            subject="수학",
            key_concept="삼각함수"
        )
    mock_user_unknown_repository.get.assert_called_once()


# -------------------------------------------------------
# list_concepts_by_user_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_list_concepts_by_user_id_no_filter(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. repository.get_list 반환값 설정
        2. service 메서드 호출
        3. 반환 타입 및 호출 인자 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_MODEL = UserUnknownConceptModel(
        id=1,
        user_id=TEST_USER_ID,
        subject="수학",
        key_concept="삼각함수",
        unknown_concept="사인 법칙",
        unknown_concept_reason="헷갈림",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_user_unknown_repository.get_list.return_value = [TEST_MODEL]

    # 2.
    results = await user_unknown_concept_service.list_concepts_by_user_id(
        user_id=TEST_USER_ID
    )

    # 3.
    assert len(results) == 1
    assert isinstance(results[0], UserUnknownConceptWithDate)
    assert results[0].user_id == TEST_USER_ID
    mock_user_unknown_repository.get_list.assert_called_once_with(
        flt=UserUnknownConceptFilter(user_id=TEST_USER_ID, subject=None),
        convert_schema=False
    )


@pytest.mark.asyncio
async def test_list_concepts_by_user_id_with_subject_filter(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. subject 필터 포함 repository.get_list 반환값 설정
        2. service 메서드 호출
        3. 전달된 filter 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_SUBJECT = "영어"
    TEST_MODEL = UserUnknownConceptModel(
        id=1,
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
        key_concept="TEST",
        unknown_concept="TEST",
        unknown_concept_reason="TEST",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_user_unknown_repository.get_list.return_value = [TEST_MODEL]

    # 2.
    await user_unknown_concept_service.list_concepts_by_user_id(
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT
    )

    # 3.
    mock_user_unknown_repository.get_list.assert_called_once_with(
        flt=UserUnknownConceptFilter(user_id=TEST_USER_ID, subject=TEST_SUBJECT),
        convert_schema=False
    )


# -------------------------------------------------------
# create_user_unknown_concept
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_create_user_unknown_concept(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. repository.create 반환값 설정
        2. service 메서드 호출
        3. 생성 결과 및 호출 인자 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_MODEL = UserUnknownConceptModel(
        id=1,
        user_id=TEST_USER_ID,
        subject="TEST",
        key_concept="TEST",
        unknown_concept="TEST",
        unknown_concept_reason="TEST",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_user_unknown_repository.create.return_value = TEST_MODEL

    # 2.
    result = await user_unknown_concept_service.create_user_unknown_concept(
        user_id=TEST_MODEL.user_id,
        subject=TEST_MODEL.subject,
        key_concept=TEST_MODEL.key_concept,
        unknown_concept=TEST_MODEL.unknown_concept,
        unknown_concept_reason=TEST_MODEL.unknown_concept_reason
    )

    # 3.
    assert isinstance(result, UserUnknownConceptWithDate)
    assert result.subject == TEST_MODEL.subject
    assert result.unknown_concept == TEST_MODEL.unknown_concept

    mock_user_unknown_repository.create.assert_called_once()

    # create 호출 시 전달된 객체 확인
    created_obj = mock_user_unknown_repository.create.call_args[0][0]
    assert isinstance(created_obj, UserUnknownConcept)
    assert created_obj.user_id == TEST_MODEL.user_id

    # convert_schema=False로 호출되었는지 확인
    assert mock_user_unknown_repository.create.call_args[1].get('convert_schema') is False


# -------------------------------------------------------
# update_user_unknown_concept_and_reason_by_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_update_concept_success(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. 기존 개념 조회 mock 설정
        2. update_from_model 반환값 설정
        3. service 메서드 호출
        4. 업데이트 결과 검증
    """
     # 1.
    TEST_ID = 1
    ORIGINAL_MODEL = UserUnknownConceptModel(
        id=TEST_ID,
        user_id=uuid.uuid4(),
        subject="수학",
        key_concept="삼각함수",
        unknown_concept="사인",
        unknown_concept_reason="헷갈림",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_user_unknown_repository.get.return_value = ORIGINAL_MODEL

    # 2.
    UPDATED_CONCEPT = "사인 함수"
    UPDATED_REASON = "공식이 헷갈림"

    UPDATED_MODEL = ORIGINAL_MODEL
    UPDATED_MODEL.unknown_concept = UPDATED_CONCEPT
    UPDATED_MODEL.unknown_concept_reason = UPDATED_REASON
    mock_user_unknown_repository.update_from_model.return_value = UPDATED_MODEL

    # 3.
    result = await user_unknown_concept_service.update_user_unknown_concept_and_reason_by_id(
        id=TEST_ID,
        unknown_concept=UPDATED_CONCEPT,
        unknown_concept_reason=UPDATED_REASON
    )

    # 4.
    assert result.unknown_concept == UPDATED_CONCEPT
    assert result.unknown_concept_reason == UPDATED_REASON
    assert result.id == TEST_ID

    # get 호출 확인
    mock_user_unknown_repository.get.assert_called_once_with(flt=UserUnknownConceptFilter(id=TEST_ID), convert_schema=False)

    # update_from_model 호출 확인
    mock_user_unknown_repository.update_from_model.assert_called_once_with(
        ORIGINAL_MODEL,
        update={
            UserUnknownConcept.FIELD_UNKNOWN_CONCEPT: UPDATED_CONCEPT,
            UserUnknownConcept.FIELD_UNKNOWN_CONCEPT_REASON: UPDATED_REASON
        },
        convert_schema=False
    )


@pytest.mark.asyncio
async def test_update_concept_not_found(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. get None 반환 설정
        2. service 메서드 호출
        3. NotFoundException 발생 및 update 미호출 검증
    """

    # 1.
    TEST_ID = 999
    mock_user_unknown_repository.get.return_value = None

    # 2.
    with pytest.raises(UserUnknownConceptNotFoundException):
        await user_unknown_concept_service.update_user_unknown_concept_and_reason_by_id(
            id=TEST_ID,
            unknown_concept="fail",
            unknown_concept_reason=None
        )

    # 3.
    mock_user_unknown_repository.get.assert_called_once_with(flt=UserUnknownConceptFilter(id=TEST_ID), convert_schema=False)
    mock_user_unknown_repository.update_from_model.assert_not_called()


# -------------------------------------------------------
# delete_by_user_id
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_by_user_id_only_user_id(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. service 메서드 호출
        2. delete filter 검증
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    await user_unknown_concept_service.delete_by_user_id(
        user_id=TEST_USER_ID
    )

    # 2.
    mock_user_unknown_repository.delete.assert_called_once()
    args, _ = mock_user_unknown_repository.delete.call_args
    flt = args[0]
    assert isinstance(flt, UserUnknownConceptFilter)
    assert flt.user_id == TEST_USER_ID
    assert flt.subject is None
    assert flt.key_concept is None


@pytest.mark.asyncio
async def test_delete_by_user_id_with_all_filters(
    user_unknown_concept_service: UserUnknownConceptService,
    mock_user_unknown_repository: AsyncMock,
):
    """
        1. subject, key_concept 포함 service 메서드 호출
        2. delete filter 검증
    """

    TEST_USER_ID = uuid.uuid4()
    TEST_SUBJECT = "테스트"
    TEST_KEY_CONCEPT = "테스트"

    await user_unknown_concept_service.delete_by_user_id(
        user_id=TEST_USER_ID,
        subject=TEST_SUBJECT,
        key_concept=TEST_KEY_CONCEPT,
    )

    # 2.
    mock_user_unknown_repository.delete.assert_called_once()
    args, _ = mock_user_unknown_repository.delete.call_args
    flt = args[0]
    assert flt.user_id == TEST_USER_ID
    assert flt.subject == TEST_SUBJECT
    assert flt.key_concept == TEST_KEY_CONCEPT
