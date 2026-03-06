# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime, timedelta

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from chats.database.repository.chat_problem_repository import ChatProblemRepository
from chats.database.repository.chat_repository import ChatFilter, ChatRepository
from chats.domain.chat import Chat
from chats.domain.chat_problem import ChatProblem, ProblemStatus
from goals.database.repository import GoalRepository
from goals.domain.goal import Goal, GoalStatus
from problems.domain.problem import GradeEnum, SubjectEnum


@pytest.fixture
def chat_repo(db_session: AsyncSession) -> ChatRepository:
    return ChatRepository(
        session=db_session
    )

@pytest.fixture
def goal_repo(db_session: AsyncSession) -> GoalRepository:
    return GoalRepository(
        session=db_session
    )

@pytest.fixture
def chat_problem_repo(db_session: AsyncSession) -> ChatProblemRepository:
    return ChatProblemRepository(
        session=db_session
    )


# -----------------------------------------------------
# get_chat_list
# -----------------------------------------------------
@pytest.mark.asyncio
async def test_get_chat_list_basic(
    chat_repo: ChatRepository,
):
    """
    1. 동일 user의 Chat 여러 개 생성
    2. get_chat_list 호출
    3. 전체 개수 반환 확인
    4. has_problem / has_active_goal 필드 존재 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    now = datetime.now()

    for i in range(5):
        await chat_repo.create(
            Chat(
                title=f"test-{i}",
                user_id=TEST_USER_ID,
                grade=GradeEnum.ELEMENTARY_FIRST,
                subject=SubjectEnum.SCIENCE,
                latest_used_at=now - timedelta(minutes=i),
            )
        )

    # 2.
    result = await chat_repo.get_chat_list(
        flt=ChatFilter(user_id=TEST_USER_ID),
        size=10,
        cursor_id=None,
        cursor_latest_used_at=None,
    )

    # 3.
    assert len(result) == 5

    # 4.
    assert all(hasattr(r, "has_problem") for r in result)
    assert all(hasattr(r, "has_active_goal") for r in result)


@pytest.mark.asyncio
async def test_get_chat_list_with_size_limit(
    chat_repo: ChatRepository,
):
    """
    1. Chat 여러 개 생성
    2. size 제한으로 조회
    3. 제한된 개수 반환 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    now = datetime.now()

    for i in range(5):
        await chat_repo.create(
            Chat(
                title=f"test-{i}",
                user_id=TEST_USER_ID,
                grade=GradeEnum.ELEMENTARY_FIRST,
                subject=SubjectEnum.SCIENCE,
                latest_used_at=now - timedelta(minutes=i),
            )
        )

    # 2.
    result = await chat_repo.get_chat_list(
        flt=ChatFilter(user_id=TEST_USER_ID),
        size=4,
        cursor_id=None,
        cursor_latest_used_at=None,
    )

    # 3.
    assert len(result) == 4


@pytest.mark.asyncio
async def test_get_chat_list_with_active_goal(
    chat_repo: ChatRepository,
    goal_repo: GoalRepository,
):
    """
    1. Chat 여러 개 생성
    2. 특정 Chat에 ACTIVE Goal 생성
    3. get_chat_list 호출
    4. 해당 Chat의 has_active_goal=True 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    now = datetime.now()

    chats: list[Chat] = []
    for i in range(5):
        chats.append(
            await chat_repo.create(
                Chat(
                    title=f"test-{i}",
                    user_id=TEST_USER_ID,
                    grade=GradeEnum.ELEMENTARY_FIRST,
                    subject=SubjectEnum.SCIENCE,
                    latest_used_at=now - timedelta(minutes=i),
                )
            )
        )

    # 2.
    await goal_repo.create(
        Goal(
            subject=SubjectEnum.SCIENCE,
            user_id=TEST_USER_ID,
            chat_id=chats[0].id,
            goal_count=10,
            solved_count=0,
            status=GoalStatus.ACTIVE,
        )
    )

    # 3.
    result = await chat_repo.get_chat_list(
        flt=ChatFilter(user_id=TEST_USER_ID),
        size=10,
        cursor_id=None,
        cursor_latest_used_at=None,
    )

    # 4.
    target = next(r for r in result if r.id == chats[0].id)
    assert target.has_active_goal is True


@pytest.mark.asyncio
async def test_get_chat_list_with_problem(
    chat_repo: ChatRepository,
    chat_problem_repo: ChatProblemRepository,
):
    """
    1. Chat 여러 개 생성
    2. 특정 Chat에 ChatProblem 생성
    3. get_chat_list 호출
    4. 해당 Chat의 has_problem=True 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    now = datetime.now()

    chats: list[Chat] = []
    for i in range(5):
        chats.append(
            await chat_repo.create(
                Chat(
                    title=f"test-{i}",
                    user_id=TEST_USER_ID,
                    grade=GradeEnum.ELEMENTARY_FIRST,
                    subject=SubjectEnum.SCIENCE,
                    latest_used_at=now - timedelta(minutes=i),
                )
            )
        )

    # 2.
    await chat_problem_repo.create(
        ChatProblem(
            chat_id=chats[0].id,
            problem_id="P-1",
            user_id=TEST_USER_ID,
            number=1,
            status=ProblemStatus.UNSOLVED,
            last_answer=None,
            is_bookmarked=False,
            bookmarked_at=None,
        )
    )

    # 3.
    result = await chat_repo.get_chat_list(
        flt=ChatFilter(user_id=TEST_USER_ID),
        size=10,
        cursor_id=None,
        cursor_latest_used_at=None,
    )

    # 4.
    target = next(r for r in result if r.id == chats[0].id)
    assert target.has_problem is True


@pytest.mark.asyncio
async def test_get_chat_list_with_cursor(
    chat_repo: ChatRepository,
):
    """
    1. Chat 여러 개 생성 (latest_used_at 기준 정렬)
    2. 첫 페이지 조회
    3. cursor 기준 두 번째 페이지 조회
    4. 중복 없이 다음 데이터 반환 확인
    """

    # 1.
    TEST_USER_ID = uuid.uuid4()
    now = datetime.now()

    for i in range(5):
        await chat_repo.create(
            Chat(
                title=f"test-{i}",
                user_id=TEST_USER_ID,
                grade=GradeEnum.ELEMENTARY_FIRST,
                subject=SubjectEnum.SCIENCE,
                latest_used_at=now - timedelta(minutes=i),
            )
        )

    # 2.
    first_page = await chat_repo.get_chat_list(
        flt=ChatFilter(user_id=TEST_USER_ID),
        size=2,
        cursor_id=None,
        cursor_latest_used_at=None,
    )

    assert len(first_page) == 2

    # 3.
    last = first_page[-1]
    second_page = await chat_repo.get_chat_list(
        flt=ChatFilter(user_id=TEST_USER_ID),
        size=2,
        cursor_id=last.id,
        cursor_latest_used_at=last.latest_used_at,
    )

    # 4.
    assert len(second_page) == 2
    assert second_page[0].id != first_page[0].id
