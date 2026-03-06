# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from chats.domain.chat import Chat
from chats.domain.chat_problem import ChatProblem, ProblemStatus
from chats.presentation.schemas.request_dto import ChatProblemSubmitRequestBody
from chats.presentation.schemas.response_dto import (
    ChatProblemDetailResponse,
    ChatProblemResponse,
    ChatProblemSubmitResponse,
)
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import AlreadySolvedException, ChatAccessForbiddenException, ChatNotFoundException
from chats.usecase.chat_problem_usecase import ChatProblemUseCase
from goals.domain.goal import Goal, GoalStatus
from goals.service.goal_service import GoalService
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
def mock_chat_service():
    return AsyncMock(spec=ChatService)

@pytest.fixture
def mock_chat_problem_service():
    return AsyncMock(spec=ChatProblemService)

@pytest.fixture
def mock_problem_service():
    return AsyncMock(spec=ProblemService)

@pytest.fixture
def mock_goal_service():
    return AsyncMock(spec=GoalService)

@pytest.fixture
def chat_problem_use_case(
    mock_chat_service,
    mock_chat_problem_service,
    mock_problem_service,
    mock_goal_service
):
    return ChatProblemUseCase(
        chat_service=mock_chat_service,
        chat_problem_service=mock_chat_problem_service,
        problem_service=mock_problem_service,
        goal_service=mock_goal_service,
    )


# =========================================================
# get_chat_problems
# =========================================================

@pytest.mark.asyncio
async def test_get_chat_problems_success(
    chat_problem_use_case: ChatProblemUseCase,
    mock_chat_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 정상 소유자의 Chat 이 존재한다
    2. get_chat_problems 를 호출한다
    3. ChatProblemResponse 리스트를 반환한다
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 1

    TEST_CHAT = Chat(
        id=TEST_CHAT_ID,
        title="test",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )
    mock_chat_service.get_chat_by_id.return_value = TEST_CHAT

    TEST_CHAT_PROBLEM = AsyncMock()
    TEST_CHAT_PROBLEM.problem_id = "p1"
    TEST_CHAT_PROBLEM.number = 1
    TEST_CHAT_PROBLEM.status = ProblemStatus.UNSOLVED
    TEST_CHAT_PROBLEM.problem.category = "ALGEBRA"
    TEST_CHAT_PROBLEM.problem.grade = "10"
    TEST_CHAT_PROBLEM.problem.level = 3

    mock_chat_problem_service.get_chat_problems_with_detail.return_value = [
        TEST_CHAT_PROBLEM
    ]

    # 2.
    res = await chat_problem_use_case.get_chat_problems(
        TEST_CHAT_ID,
        TEST_USER_ID,
    )

    assert isinstance(res, list)
    assert len(res) == 1
    assert isinstance(res[0], ChatProblemResponse)
    assert res[0].id == "p1"

    mock_chat_service.get_chat_by_id.assert_called_once_with(TEST_CHAT_ID)
    mock_chat_problem_service.get_chat_problems_with_detail.assert_called_once_with(
        TEST_CHAT_ID
    )


@pytest.mark.asyncio
async def test_get_chat_problems_wrong_user(
    chat_problem_use_case: ChatProblemUseCase,
    mock_chat_service: AsyncMock,
):
    """
    1. 다른 유저의 Chat 이 존재한다
    2. get_chat_problems 를 호출한다
    3. ChatAccessForbiddenException 이 발생한다
    """

    # 1.
    TEST_MY_USER_ID = uuid.uuid4()
    TEST_OTHER_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 1

    # 2.
    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="x",
        user_id=TEST_OTHER_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    # 3.
    with pytest.raises(ChatAccessForbiddenException):
        await chat_problem_use_case.get_chat_problems(
            TEST_CHAT_ID,
            TEST_MY_USER_ID,
        )


# =========================================================
# get_chat_problem
# =========================================================

@pytest.mark.asyncio
async def test_get_chat_problem_success(
    chat_problem_use_case: ChatProblemUseCase,
    mock_chat_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
    mock_problem_service: AsyncMock,
):
    """
    1. Chat, ChatProblem, Problem 이 존재한다
    2. get_chat_problem 을 호출한다
    3. ChatProblemDetailResponse 를 반환한다
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 10
    TEST_PROBLEM_ID = "p100"

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="chat",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    TEST_CHAT_PROBLEM = ChatProblem(
        id=123,
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        number=3,
        status=ProblemStatus.WRONG,
        last_answer="5",
        is_bookmarked=False,
        bookmarked_at=None,
    )
    mock_chat_problem_service.get_chat_problem.return_value = TEST_CHAT_PROBLEM

    mock_problem_service.get_problem_by_id.return_value = Problem(
        id=TEST_PROBLEM_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="이것은 테스트 문제입니다.",
        url=None,
        primary=None,
        secondary=None,
        specific=None,
        category=None,
        choices=None,
        explanation=None,
        tags=None,
        hint=None,
        correct_answers=[Answer(answer="정답입니다", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )

    # 2.
    res = await chat_problem_use_case.get_chat_problem(
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
    )

    # 3.
    assert isinstance(res, ChatProblemDetailResponse)
    assert res.number == 3
    assert res.status == ProblemStatus.WRONG

    mock_problem_service.get_problem_by_id.assert_called_once_with(
        TEST_PROBLEM_ID
    )


# =========================================================
# submit_answer
# =========================================================

@pytest.mark.asyncio
async def test_submit_answer_correct_with_active_goal(
    chat_problem_use_case: ChatProblemUseCase,
    mock_chat_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
    mock_problem_service: AsyncMock,
    mock_goal_service: AsyncMock,
):
    """
    1. 미해결 문제와 활성 Goal 이 존재한다
    2. submit_answer 를 호출한다
    3. 정답 처리 및 Goal 이 반환된다
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 1
    TEST_PROBLEM_ID = "p1"

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="chat",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    TEST_CHAT_PROBLEM = AsyncMock()
    TEST_CHAT_PROBLEM.id = 10
    TEST_CHAT_PROBLEM.problem_id = TEST_PROBLEM_ID
    TEST_CHAT_PROBLEM.status = ProblemStatus.UNSOLVED
    mock_chat_problem_service.get_chat_problem.return_value = TEST_CHAT_PROBLEM

    mock_problem_service.submit_problem_answer.return_value = True

    TEST_GOAL = Goal(
        id=1,
        user_id=TEST_USER_ID,
        chat_id=TEST_CHAT_ID,
        subject=SubjectEnum.MATH,
        goal_count=10,
        solved_count=3,
        status=GoalStatus.ACTIVE,
        finished_at=None,
    )
    mock_goal_service.get_goal_by_chat_id.return_value = TEST_GOAL
    mock_goal_service.update_solved_count.return_value = TEST_GOAL

    TEST_REQUEST = ChatProblemSubmitRequestBody(
        answer={
            "type": "단일선택 객관식",
            "answer": 3,
        }
    )

    # 2.
    res = await chat_problem_use_case.submit_answer(
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        req=TEST_REQUEST,
        user_id=TEST_USER_ID,
    )

    # 3.
    assert isinstance(res, ChatProblemSubmitResponse)
    assert res.is_correct is True
    assert res.active_goal is not None

    mock_chat_problem_service.update_chat_problem_status.assert_called_once()
    mock_chat_service.update_chat_latest_used_at.assert_called_once_with(
        TEST_CHAT_ID
    )


@pytest.mark.asyncio
async def test_submit_answer_already_solved(
    chat_problem_use_case: ChatProblemUseCase,
    mock_chat_service: AsyncMock,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 이미 해결된 ChatProblem 이 존재한다
    2. submit_answer 를 호출한다
    3. AlreadySolvedException 이 발생한다
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 1
    TEST_PROBLEM_ID = "p1"

    mock_chat_service.get_chat_by_id.return_value = Chat(
        id=TEST_CHAT_ID,
        title="chat",
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )

    TEST_CHAT_PROBLEM = AsyncMock()
    TEST_CHAT_PROBLEM.problem_id = TEST_PROBLEM_ID
    TEST_CHAT_PROBLEM.status = ProblemStatus.CORRECT
    mock_chat_problem_service.get_chat_problem.return_value = TEST_CHAT_PROBLEM

    TEST_REQUEST = ChatProblemSubmitRequestBody(
        answer={
            "type": "단일선택 객관식",
            "answer": 3,
        }
    )

    # 2. & 3.
    with pytest.raises(AlreadySolvedException):
        await chat_problem_use_case.submit_answer(
            chat_id=TEST_CHAT_ID,
            problem_id=TEST_PROBLEM_ID,
            req=TEST_REQUEST,
            user_id=TEST_USER_ID,
        )
