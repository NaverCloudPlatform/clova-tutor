# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from sqlalchemy.exc import IntegrityError

from chats.database.models import ChatProblemModel
from chats.database.repository.chat_problem_repository import ChatProblemRepository
from chats.domain.chat import Chat
from chats.domain.chat_problem import ChatProblem, ProblemStatus
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import (
    ChatProblemAllProblemRecommendedException,
    ChatProblemDuplicateException,
    ChatProblemNotFoundException,
)
from problems.domain.problem import (
    Answer,
    GradeEnum,
    Problem,
    ProblemAnswerType,
    ProblemLevel,
    SubjectEnum,
)
from problems.service.problem_service import ProblemService


@pytest.fixture
def mock_chat_problem_repo() -> AsyncMock:
    return AsyncMock(spec=ChatProblemRepository)

@pytest.fixture
def mock_chat_service() -> AsyncMock:
    return AsyncMock(spec=ChatService)

@pytest.fixture
def mock_problem_service() -> AsyncMock:
    return AsyncMock(spec=ProblemService)

@pytest.fixture
def chat_problem_service(
    mock_chat_problem_repo,
    mock_chat_service,
    mock_problem_service
) -> ChatProblemService:
    return ChatProblemService(
        chat_problem_repo=mock_chat_problem_repo,
        chat_service=mock_chat_service,
        problem_service=mock_problem_service
    )


# -------------------------------------------------------
# exists_by_chat_id
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_exists_by_chat_id_true(chat_problem_service, mock_chat_problem_repo):
    """
    1. 특정 chat_id 에 대한 ChatProblem 이 존재하도록 조건 준비
    2. exists_by_chat_id 호출
    3. True 반환 및 repository 호출 인자 검증
    """
    # 1.
    mock_chat_problem_repo.exists.return_value = True

    # 2.
    result = await chat_problem_service.exists_by_chat_id(10)

    # 3.
    assert result is True
    mock_chat_problem_repo.exists.assert_called_once()
    _, kwargs = mock_chat_problem_repo.exists.call_args
    assert kwargs["flt"].chat_id == 10


@pytest.mark.asyncio
async def test_exists_by_chat_id_false(chat_problem_service, mock_chat_problem_repo):
    """
    1. 특정 chat_id 에 대한 ChatProblem 이 존재하지 않도록 조건 준비
    2. exists_by_chat_id 호출
    3. False 반환 확인
    """
    # 1.
    mock_chat_problem_repo.exists.return_value = False

    # 2.
    result = await chat_problem_service.exists_by_chat_id(10)

    # 3.
    assert result is False


# -------------------------------------------------------
# exists_by_problem_id
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_exists_by_problem_id(chat_problem_service, mock_chat_problem_repo):
    """
    1. problem_id + chat_id + user_id 조건에 맞는 ChatProblem 이 존재하도록 준비
    2. exists_by_problem_id 호출
    3. True 반환 및 전달된 필터 조건 검증
    """
    # 1.
    TEST_USER_ID = uuid4()
    mock_chat_problem_repo.exists.return_value = True

    # 2.
    result = await chat_problem_service.exists_by_problem_id(
        problem_id="P123",
        chat_id=99,
        user_id=TEST_USER_ID,
        is_bookmarked=True
    )

    # 3.
    assert result is True
    mock_chat_problem_repo.exists.assert_called_once()
    _, kwargs = mock_chat_problem_repo.exists.call_args
    flt = kwargs["flt"]
    assert flt.problem_id == "P123"
    assert flt.chat_id == 99
    assert flt.user_id == TEST_USER_ID
    assert flt.is_bookmarked is True


# -------------------------------------------------------
# get_bookmarked_problems
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_bookmarked_problems(chat_problem_service, mock_chat_problem_repo):
    """
    1. 북마크된 문제 리스트 반환 조건 준비
    2. get_bookmarked_problems 호출
    3. 반환값 및 repository 호출 여부 확인
    """
    # 1.
    TEST_USER_ID = uuid4()
    TEST_PROBLEMS = [AsyncMock()]
    mock_chat_problem_repo.get_bookmarked_problems.return_value = TEST_PROBLEMS

    # 2.
    result = await chat_problem_service.get_bookmarked_problems(
        user_id=TEST_USER_ID,
        subject=[SubjectEnum.MATH],
        status=[ProblemStatus.UNSOLVED],
        size=10,
        cursor_bookmarked_at=None
    )

    # 3.
    assert result == TEST_PROBLEMS
    mock_chat_problem_repo.get_bookmarked_problems.assert_called_once()


# -------------------------------------------------------
# add_problem_to_chat
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_add_problem_to_chat_first(chat_problem_service, mock_chat_problem_repo):
    """
    1. 기존 ChatProblem 이 없는 상태 준비
    2. add_problem_to_chat 호출
    3. number 가 1 인 ChatProblem 생성 확인
    """
    # 1.
    mock_chat_problem_repo.get_list.return_value = []
    TEST_CHAT_PROBLEM = ChatProblem(
        chat_id=1,
        problem_id="P1",
        status=ProblemStatus.UNSOLVED,
        user_id=uuid4(),
        last_answer=None,
        number=1,
        is_bookmarked=False,
        bookmarked_at=None
    )
    mock_chat_problem_repo.create.return_value = TEST_CHAT_PROBLEM

    # 2.
    result = await chat_problem_service.add_problem_to_chat(
        chat_id=1,
        problem_id="P1",
        user_id=uuid4()
    )

    # 3.
    assert result.number == 1
    mock_chat_problem_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_add_problem_to_chat_duplicate(chat_problem_service, mock_chat_problem_repo):
    """
    1. ChatProblem 생성 시 중복 에러가 발생하도록 조건 준비
    2. add_problem_to_chat 호출
    3. ChatProblemDuplicateException 발생 확인
    """
    # 1.
    mock_chat_problem_repo.get_list.return_value = []
    mock_chat_problem_repo.create.side_effect = IntegrityError("err", "params", "orig")

    # 2. / 3.
    with pytest.raises(ChatProblemDuplicateException):
        await chat_problem_service.add_problem_to_chat(
            chat_id=1,
            problem_id="P1",
            user_id=uuid4()
        )


# -------------------------------------------------------
# get_chat_problems
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_chat_problems(chat_problem_service, mock_chat_problem_repo):
    """
    1. 특정 chat_id 에 대한 ChatProblem 리스트 준비
    2. get_chat_problems 호출
    3. 반환값 검증
    """
    # 1.
    TEST_CHAT_PROBLEMS = [AsyncMock()]
    mock_chat_problem_repo.get_list.return_value = TEST_CHAT_PROBLEMS

    # 2.
    result = await chat_problem_service.get_chat_problems(1)

    # 3.
    assert result == TEST_CHAT_PROBLEMS
    mock_chat_problem_repo.get_list.assert_called_once()


# -------------------------------------------------------
# get_chat_problem
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_chat_problem_success(chat_problem_service, mock_chat_problem_repo):
    """
    1. 특정 chat_id + problem_id 에 해당하는 ChatProblem 준비
    2. get_chat_problem 호출
    3. 정상적으로 ChatProblem 반환 확인
    """
    # 1.
    TEST_CHAT_PROBLEM = ChatProblem(
        chat_id=1,
        problem_id="P1",
        status=ProblemStatus.UNSOLVED,
        user_id=uuid4(),
        last_answer=None,
        number=1,
        is_bookmarked=False,
        bookmarked_at=None
    )
    mock_chat_problem_repo.get.return_value = TEST_CHAT_PROBLEM

    # 2.
    result = await chat_problem_service.get_chat_problem(1, "P1")

    # 3.
    assert result.problem_id == "P1"


@pytest.mark.asyncio
async def test_get_chat_problem_not_found(chat_problem_service, mock_chat_problem_repo):
    """
    1. ChatProblem 이 존재하지 않도록 조건 준비
    2. get_chat_problem 호출
    3. ChatProblemNotFoundException 발생 확인
    """
    # 1.
    mock_chat_problem_repo.get.return_value = None

    # 2. / 3.
    with pytest.raises(ChatProblemNotFoundException):
        await chat_problem_service.get_chat_problem(1, "P123")


# -------------------------------------------------------
# get_chat_problems_with_detail
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_chat_problems_with_detail(chat_problem_service, mock_chat_problem_repo):
    """
    1. 문제 상세 정보를 포함한 ChatProblem 리스트 준비
    2. get_chat_problems_with_detail 호출
    3. 반환값 검증
    """
    # 1.
    TEST_CHAT_PROBLEMS = [AsyncMock()]
    mock_chat_problem_repo.get_with_problems.return_value = TEST_CHAT_PROBLEMS

    # 2.
    result = await chat_problem_service.get_chat_problems_with_detail(10)

    # 3.
    assert result == TEST_CHAT_PROBLEMS
    mock_chat_problem_repo.get_with_problems.assert_called_once()


# -------------------------------------------------------
# get_chat_problem_detail
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_chat_problem_detail(
    chat_problem_service,
    mock_chat_problem_repo,
    mock_problem_service
):
    """
    1. ChatProblem 과 Problem 이 모두 존재하도록 조건 준비
    2. get_chat_problem_detail 호출
    3. Problem 정보가 결합된 결과 반환 확인
    """
    # 1.
    TEST_CHAT_PROBLEM = ChatProblem(
        chat_id=1,
        problem_id="P1",
        status=ProblemStatus.UNSOLVED,
        user_id=uuid4(),
        last_answer=None,
        number=1,
        is_bookmarked=False,
        bookmarked_at=None
    )
    mock_chat_problem_repo.get.return_value = TEST_CHAT_PROBLEM

    TEST_PROBLEM = Problem(
        id="P1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="정답", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1
    )
    mock_problem_service.get_problem_by_id.return_value = TEST_PROBLEM

    # 2.
    result = await chat_problem_service.get_chat_problem_detail(1, "P1")

    # 3.
    assert result.problem_id == "P1"
    mock_problem_service.get_problem_by_id.assert_called_once()


# -------------------------------------------------------
# find_not_duplicate_problem
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_find_not_duplicate_problem(
    chat_problem_service,
    mock_chat_problem_repo,
    mock_chat_service,
    mock_problem_service
):
    """
    1. 이미 추천된 문제를 제외한 새로운 문제가 존재하도록 조건 준비
    2. find_not_duplicate_problem 호출
    3. 중복되지 않은 Problem 반환 확인
    """
    # 1.
    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=1,
        title="t",
        user_id=uuid4(),
        subject=SubjectEnum.MATH,
        grade=GradeEnum.ELEMENTARY_FIRST,
        latest_used_at=datetime.now()
    )
    mock_chat_problem_repo.get_list.return_value = [
        ChatProblem(
            chat_id=1,
            problem_id="P1",
            status=ProblemStatus.UNSOLVED,
            user_id=uuid4(),
            last_answer=None,
            number=1,
            is_bookmarked=False,
            bookmarked_at=None
        )
    ]
    mock_problem_service.find_random_problem.return_value = Problem(
        id="P2",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="문제",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="정답", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1
    )

    # 2.
    result = await chat_problem_service.find_not_duplicate_problem(1)

    # 3.
    assert result.id == "P2"


@pytest.mark.asyncio
async def test_find_not_duplicate_problem_none(
    chat_problem_service,
    mock_chat_problem_repo,
    mock_chat_service,
    mock_problem_service
):
    """
    1. 추천 가능한 문제가 더 이상 존재하지 않도록 조건 준비
    2. find_not_duplicate_problem 호출
    3. ChatProblemAllProblemRecommendedException 발생 확인
    """
    # 1.
    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=1,
        title="t",
        user_id=uuid4(),
        subject=SubjectEnum.MATH,
        grade=GradeEnum.ELEMENTARY_FIRST,
        latest_used_at=datetime.now()
    )
    mock_chat_problem_repo.get_list.return_value = []
    mock_problem_service.find_random_problem.return_value = None

    # 2. / 3.
    with pytest.raises(ChatProblemAllProblemRecommendedException):
        await chat_problem_service.find_not_duplicate_problem(1)


# -------------------------------------------------------
# update_bookmark
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_update_bookmark_success(chat_problem_service, mock_chat_problem_repo):
    """
    1. 수정 대상 ChatProblem 이 존재하도록 조건 준비
    2. update_bookmark 호출
    3. 북마크 상태가 반영된 ChatProblem 반환 확인
    """
    # 1.
    mock_chat_problem_repo.get.return_value = ChatProblemModel()
    UPDATED = ChatProblem(
        chat_id=1,
        problem_id="P1",
        status=ProblemStatus.UNSOLVED,
        user_id=uuid4(),
        last_answer=None,
        number=1,
        is_bookmarked=True,
        bookmarked_at=datetime.now()
    )
    mock_chat_problem_repo.update_from_model.return_value = UPDATED

    # 2.
    result = await chat_problem_service.update_bookmark(
        chat_id=1,
        problem_id="P1",
        user_id=uuid4(),
        is_bookmarked=True,
        bookmarked_at=datetime.now()
    )

    # 3.
    assert result.is_bookmarked is True
    mock_chat_problem_repo.update_from_model.assert_called_once()


@pytest.mark.asyncio
async def test_update_bookmark_not_found(chat_problem_service, mock_chat_problem_repo):
    """
    1. 수정 대상 ChatProblem 이 존재하지 않도록 조건 준비
    2. update_bookmark 호출
    3. ChatProblemNotFoundException 발생 확인
    """
    # 1.
    mock_chat_problem_repo.get.return_value = None

    # 2. / 3.
    with pytest.raises(ChatProblemNotFoundException):
        await chat_problem_service.update_bookmark(
            chat_id=1,
            problem_id="P1",
            user_id=uuid4(),
            is_bookmarked=True,
            bookmarked_at=None
        )


# -------------------------------------------------------
# update_chat_problem_status
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_update_chat_problem_status_success(chat_problem_service, mock_chat_problem_repo):
    """
    1. 수정 대상 ChatProblem 이 존재하도록 조건 준비
    2. update_chat_problem_status 호출
    3. 상태가 변경된 ChatProblem 반환 확인
    """
    # 1.
    mock_chat_problem_repo.get.return_value = ChatProblemModel()
    UPDATED = ChatProblem(
        chat_id=1,
        problem_id="P1",
        status=ProblemStatus.UNSOLVED,
        user_id=uuid4(),
        last_answer="ans",
        number=1,
        is_bookmarked=False,
        bookmarked_at=None
    )
    mock_chat_problem_repo.update_from_model.return_value = UPDATED

    # 2.
    result = await chat_problem_service.update_chat_problem_status(
        chat_problem_id=1,
        status=ProblemStatus.UNSOLVED,
        last_answer="ans"
    )

    # 3.
    assert result.status == ProblemStatus.UNSOLVED


# -------------------------------------------------------
# delete_chat_problems_by_chat_id
# -------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_chat_problems_by_chat_id(chat_problem_service, mock_chat_problem_repo):
    """
    1. 삭제 대상 chat_id 조건 준비
    2. delete_chat_problems_by_chat_id 호출
    3. repository.delete 가 올바른 필터로 호출되었는지 확인
    """
    # 1.
    TEST_CHAT_ID = 5

    # 2.
    await chat_problem_service.delete_chat_problems_by_chat_id(TEST_CHAT_ID)

    # 3.
    mock_chat_problem_repo.delete.assert_called_once()
    _, kwargs = mock_chat_problem_repo.delete.call_args
    assert kwargs["flt"].chat_id == TEST_CHAT_ID
