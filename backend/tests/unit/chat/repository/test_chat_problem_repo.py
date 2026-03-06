# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime, timedelta

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from chats.database.repository.chat_problem_repository import (
    ChatProblemFilter,
    ChatProblemRepository,
)
from chats.database.repository.chat_repository import ChatRepository
from chats.domain.chat import Chat
from chats.domain.chat_problem import ChatProblem, ProblemStatus
from goals.database.repository import GoalRepository
from goals.domain.goal import Goal, GoalStatus
from problems.database.repository import ProblemRepository
from problems.domain.problem import (
    Answer,
    GradeEnum,
    Problem,
    ProblemAnswerType,
    ProblemLevel,
    SubjectEnum,
)


@pytest.fixture
def chat_problem_repo(db_session: AsyncSession) -> ChatProblemRepository:
    return ChatProblemRepository(
        session=db_session
    )

@pytest.fixture
def problem_repo(db_session: AsyncSession) -> ProblemRepository:
    return ProblemRepository(
        session=db_session
    )

@pytest.fixture
def goal_repo(db_session: AsyncSession) -> GoalRepository:
    return GoalRepository(
        session=db_session
    )

@pytest.fixture
def chat_repo(db_session: AsyncSession) -> ChatRepository:
    return ChatRepository(
        session=db_session
    )

# -----------------------------------------------------
# exists
# -----------------------------------------------------

@pytest.mark.asyncio
async def test_chat_problem_exists_false(
    chat_problem_repo: ChatProblemRepository,
):
    """
    1. 존재하지 않는 ChatProblem 조건 준비
    2. exists 호출
    3. False 반환 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()

    # 2.
    exists_found = await chat_problem_repo.exists(
        ChatProblemFilter(
            chat_id=-1,
            problem_id="P-1",
            user_id=TEST_USER_ID,
        )
    )

    # 3.
    assert exists_found is False


@pytest.mark.asyncio
async def test_chat_problem_exists_true(
    chat_problem_repo: ChatProblemRepository,
):
    """
    1. ChatProblem 생성
    2. 동일 조건으로 exists 호출
    3. True 반환 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()

    chat_problem = ChatProblem(
        chat_id=-1,
        problem_id="P-1",
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=False,
        bookmarked_at=None,
    )
    await chat_problem_repo.create(chat_problem)

    # 2.
    exists_found = await chat_problem_repo.exists(
        ChatProblemFilter(
            chat_id=-1,
            problem_id="P-1",
            user_id=TEST_USER_ID,
        )
    )

    # 3.
    assert exists_found is True


# -----------------------------------------------------
# get_with_problems : Problem detail을 포함하여 반환
# -----------------------------------------------------
@pytest.mark.asyncio
async def test_get_with_problems_returns_problem_detail(
    chat_problem_repo: ChatProblemRepository,
    problem_repo: ProblemRepository,
):
    """
    1. Problem 생성
    2. ChatProblem 생성
    3. get_with_problems 호출
    4. Problem 정보가 포함되어 반환되는지 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = -1

    problem = Problem(
        id="P-1",
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
    await problem_repo.create(problem)

    # 2.
    chat_problem = ChatProblem(
        chat_id=TEST_CHAT_ID,
        problem_id="P-1",
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=False,
        bookmarked_at=None,
    )
    await chat_problem_repo.create(chat_problem)

    # 3.
    result = await chat_problem_repo.get_with_problems(
        ChatProblemFilter(chat_id=TEST_CHAT_ID)
    )

    # 4.
    assert len(result) == 1
    assert result[0].problem is not None
    assert result[0].problem.id == "P-1"


# -----------------------------------------------------
# get_bookmarked_problems : ACTIVE Goal이 있는 경우
# -----------------------------------------------------
@pytest.mark.asyncio
async def test_get_bookmarked_problems_has_active_goal_true(
    chat_problem_repo: ChatProblemRepository,
    goal_repo: GoalRepository,
    problem_repo: ProblemRepository,
    chat_repo: ChatRepository,
):
    """
    1. Chat 생성
    2. Problem + ChatProblem(북마크) 생성
    3. ACTIVE Goal 생성
    4. get_bookmarked_problems 호출
    5. has_active_goal=True 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()

    chat = await chat_repo.create(
        Chat(
            title="test",
            user_id=TEST_USER_ID,
            grade=GradeEnum.ELEMENTARY_FIRST,
            subject=SubjectEnum.SCIENCE,
            latest_used_at=datetime.now(),
        )
    )

    # 2.
    problem = Problem(
        id="P-1",
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        problem="테스트 문제",
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
        semester=1,
    )
    await problem_repo.create(problem)

    now = datetime.now()
    chat_problem = ChatProblem(
        chat_id=chat.id,
        problem_id="P-1",
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=True,
        bookmarked_at=now,
    )
    await chat_problem_repo.create(chat_problem)

    # 3.
    goal = Goal(
        subject=SubjectEnum.SCIENCE,
        user_id=TEST_USER_ID,
        chat_id=chat.id,
        goal_count=10,
        solved_count=0,
        status=GoalStatus.ACTIVE,
    )
    await goal_repo.create(goal)

    # 4.
    result = await chat_problem_repo.get_bookmarked_problems(
        ChatProblemFilter(user_id=TEST_USER_ID),
        cursor_bookmarked_at=None,
        size=10,
    )

    # 5.
    assert len(result) == 1
    assert result[0].chat.has_active_goal is True


# -----------------------------------------------------
# get_bookmarked_problems : cursor 기반 페이징
# -----------------------------------------------------
@pytest.mark.asyncio
async def test_get_bookmarked_problems_cursor_pagination(
    chat_problem_repo: ChatProblemRepository,
    problem_repo: ProblemRepository,
    chat_repo: ChatRepository,
):
    """
    1. Chat 생성
    2. 북마크된 ChatProblem 2개 생성 (시간 차)
    3. 첫 페이지 조회
    4. cursor 기준 두 번째 페이지 조회
    5. 시간 순 정렬 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()

    chat = await chat_repo.create(
        Chat(
            title="test",
            user_id=TEST_USER_ID,
            grade=GradeEnum.ELEMENTARY_FIRST,
            subject=SubjectEnum.SCIENCE,
            latest_used_at=datetime.now(),
        )
    )

    # 2.
    now = datetime.now()

    for i, minutes in [(1, 1), (2, 10)]:
        problem = Problem(
            id=f"P-{i}",
            subject=SubjectEnum.MATH,
            grade=GradeEnum.HIGH_FIRST,
            problem="테스트 문제",
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
            semester=1,
        )
        await problem_repo.create(problem)

        await chat_problem_repo.create(
            ChatProblem(
                chat_id=chat.id,
                problem_id=f"P-{i}",
                user_id=TEST_USER_ID,
                number=i,
                status=ProblemStatus.UNSOLVED,
                last_answer=None,
                is_bookmarked=True,
                bookmarked_at=now - timedelta(minutes=minutes),
            )
        )

    # 3.
    first_page = await chat_problem_repo.get_bookmarked_problems(
        ChatProblemFilter(user_id=TEST_USER_ID),
        cursor_bookmarked_at=None,
        size=1,
    )

    # 4.
    cursor = first_page[-1].bookmarked_at

    second_page = await chat_problem_repo.get_bookmarked_problems(
        ChatProblemFilter(user_id=TEST_USER_ID),
        cursor_bookmarked_at=cursor,
        size=1,
    )

    # 5.
    assert len(first_page) == 1
    assert len(second_page) == 1
    assert second_page[0].bookmarked_at < cursor
