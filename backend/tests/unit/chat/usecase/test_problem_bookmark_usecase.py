# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from chats.domain.chat import Chat, ChatDetail
from chats.domain.chat_problem import (
    ChatProblem,
    ChatProblemWithChatDetailAndWithProblem,
    ProblemStatus,
)
from chats.presentation.schemas.request_dto import ProblemBookmarkCreateRequestBody
from chats.presentation.schemas.response_dto import (
    ProblemBookmarkCreateResponse,
    ProblemBookmarkResponse,
    ProblemDuplicateStatus,
)
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import ChatAccessForbiddenException
from chats.usecase.problem_bookmark_usecase import ProblemBookmarkUseCase
from common.presentation.pagination import (
    CursorPaginateParams,
    CursorPaginateResponse,
    decode_cursor,
    encode_cursor,
)
from problems.domain.problem import (
    Answer,
    GradeEnum,
    Problem,
    ProblemAnswerType,
    ProblemLevel,
    SubjectEnum,
)


def _make_chat(*, id: int, user_id: uuid.UUID):  # noqa: A002
    return Chat(
        id=id,
        title="x",
        user_id=user_id,
        subject=SubjectEnum.MATH,
        grade=GradeEnum.HIGH_FIRST,
        latest_used_at=datetime.now(),
    )


@pytest.fixture
def mock_chat_problem_service() -> AsyncMock:
    """ChatProblemService Mock 객체."""
    return AsyncMock(spec=ChatProblemService)


@pytest.fixture
def mock_chat_service() -> AsyncMock:
    """ChatService Mock 객체."""
    return AsyncMock(spec=ChatService)


@pytest.fixture
def bookmark_use_case(
    mock_chat_problem_service: AsyncMock,
    mock_chat_service: AsyncMock,
) -> ProblemBookmarkUseCase:
    """ProblemBookmarkUseCase 인스턴스."""
    return ProblemBookmarkUseCase(
        chat_problem_service=mock_chat_problem_service,
        chat_service=mock_chat_service,
    )



# =======================================================
# check_problem_bookmark_duplicate
# =======================================================

@pytest.mark.asyncio
async def test_check_problem_bookmark_duplicate_duplicate(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 이미 북마크된 문제 조건 준비
    2. check_problem_bookmark_duplicate 호출
    3. DUPLICATE 상태 반환 및 서비스 호출 인자 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_PROBLEM_ID = "test123"

    mock_chat_problem_service.exists_by_problem_id.return_value = True

    # 2.
    response = await bookmark_use_case.check_problem_bookmark_duplicate(
        user_id=TEST_USER_ID,
        problem_id=TEST_PROBLEM_ID,
    )

    # 3.
    assert response.status == ProblemDuplicateStatus.DUPLICATE
    mock_chat_problem_service.exists_by_problem_id.assert_called_once_with(
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        is_bookmarked=True,
    )


@pytest.mark.asyncio
async def test_check_problem_bookmark_duplicate_unique(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 북마크되지 않은 문제 조건 준비
    2. check_problem_bookmark_duplicate 호출
    3. AVAILABLE 상태 반환 확인
    """
    # 1.

    TEST_USER_ID = uuid.uuid4()
    TEST_PROBLEM_ID = "TEST_PROBLEM_ID"

    mock_chat_problem_service.exists_by_problem_id.return_value = False

    # 2.
    result = await bookmark_use_case.check_problem_bookmark_duplicate(
        user_id=TEST_USER_ID,
        problem_id=TEST_PROBLEM_ID,
    )

    # 3.
    assert result.status == ProblemDuplicateStatus.UNIQUE


# =======================================================
# bookmark_problem
# =======================================================

@pytest.mark.asyncio
async def test_bookmark_problem_success(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
    mock_chat_service: AsyncMock,
):
    """
    1. 북마크 요청 데이터 및 반환 ChatProblem 준비
    2. bookmark_problem 호출
    3. 응답 DTO 필드 및 서비스 호출 검증
    """
    TEST_USER_ID = uuid.uuid4()
    TEST_PROBLEM_ID = "test123"
    TEST_CHAT_ID = 123
    TEST_DATE_TIME = datetime.now()

    mock_chat_service.get_chat_by_id.return_value = _make_chat(
        id=TEST_CHAT_ID, user_id=TEST_USER_ID
    )

    request_body = ProblemBookmarkCreateRequestBody(
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        is_bookmarked=True,
        bookmarked_at=TEST_DATE_TIME,
    )

    mock_chat_problem_service.update_bookmark.return_value = ChatProblem(
        id=1,
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=True,
        bookmarked_at=TEST_DATE_TIME,
    )

    response = await bookmark_use_case.bookmark_problem(
        user_id=TEST_USER_ID,
        body=request_body,
    )

    assert isinstance(response, ProblemBookmarkCreateResponse)
    assert response.chat_id == TEST_CHAT_ID
    assert response.problem_id == TEST_PROBLEM_ID
    assert response.is_bookmarked is True
    assert response.bookmarked_at.tzinfo is not None

    mock_chat_problem_service.update_bookmark.assert_called_once_with(
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        is_bookmarked=True,
        bookmarked_at=TEST_DATE_TIME,
    )


@pytest.mark.asyncio
async def test_bookmark_problem_unbookmark(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
    mock_chat_service: AsyncMock,
):
    """
    1. 북마크 해제 요청 데이터 준비
    2. bookmark_problem 호출
    3. is_bookmarked=False 상태 반환 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 123
    TEST_PROBLEM_ID = "TEST_PROBLEM_ID"
    TEST_DATE_TIME = datetime.now()

    mock_chat_service.get_chat_by_id.return_value = _make_chat(
        id=TEST_CHAT_ID, user_id=TEST_USER_ID
    )

    TEST_REQUEST_BODY = ProblemBookmarkCreateRequestBody(
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        is_bookmarked=False,
        bookmarked_at=TEST_DATE_TIME,
    )

    mock_chat_problem_service.update_bookmark.return_value = ChatProblem(
        id=1,
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=False,
        bookmarked_at=None,
    )

    # 2.
    response = await bookmark_use_case.bookmark_problem(
        user_id=TEST_USER_ID,
        body=TEST_REQUEST_BODY,
    )

    # 3.
    assert response.is_bookmarked is False


@pytest.mark.asyncio
async def test_bookmark_problem_wrong_user(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_service: AsyncMock,
):
    """
    1. 다른 사용자 소유의 채팅방에 북마크 요청
    2. bookmark_problem 호출
    3. ChatAccessForbiddenException 발생 검증
    """
    TEST_MY_USER_ID = uuid.uuid4()
    TEST_OTHER_USER_ID = uuid.uuid4()
    TEST_CHAT_ID = 456
    TEST_PROBLEM_ID = "p1"

    mock_chat_service.get_chat_by_id.return_value = _make_chat(
        id=TEST_CHAT_ID, user_id=TEST_OTHER_USER_ID
    )

    body = ProblemBookmarkCreateRequestBody(
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        is_bookmarked=True,
        bookmarked_at=datetime.now(),
    )

    with pytest.raises(ChatAccessForbiddenException):
        await bookmark_use_case.bookmark_problem(
            user_id=TEST_MY_USER_ID,
            body=body,
        )


# =======================================================
# get_bookmark_list
# =======================================================

@pytest.mark.asyncio
async def test_get_bookmark_list_no_cursor(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 커서 없는 첫 페이지 조건 준비
    2. get_bookmark_list 호출
    3. 아이템 및 cursor_bookmarked_at=None 전달 확인
    """
    TEST_USER_ID = uuid.uuid4()
    TEST_PROBLEM_ID = "test123"
    TEST_CHAT_ID = 123
    TEST_BOOKMARKED_AT = datetime.now()

    TEST_CHAT_DETAIL = MagicMock(spec=ChatDetail)
    TEST_CHAT_DETAIL.has_active_goal = True

    TEST_PROBLEM = Problem(
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
        correct_answers=[Answer(answer="1", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )

    TEST_CHAT_PROBLEM = ChatProblemWithChatDetailAndWithProblem(
        id=1,
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=True,
        bookmarked_at=TEST_BOOKMARKED_AT,
        problem=TEST_PROBLEM,
        chat=TEST_CHAT_DETAIL,
    )

    mock_chat_problem_service.get_bookmarked_problems.return_value = [
        TEST_CHAT_PROBLEM
    ]

    paginate_filter = CursorPaginateParams(size=1)

    response = await bookmark_use_case.get_bookmark_list(
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        status_list=[ProblemStatus.UNSOLVED],
        paginate_filter=paginate_filter,
    )

    assert isinstance(response, CursorPaginateResponse)
    assert len(response.items) == 1

    item = response.items[0]
    assert isinstance(item, ProblemBookmarkResponse)
    assert item.problem.number == TEST_CHAT_PROBLEM.number
    assert item.bookmarked_at.tzinfo is not None

    mock_chat_problem_service.get_bookmarked_problems.assert_called_once_with(
        user_id=TEST_USER_ID,
        subject=[SubjectEnum.MATH],
        status=[ProblemStatus.UNSOLVED],
        size=1,
        cursor_bookmarked_at=None,
    )


@pytest.mark.asyncio
async def test_get_bookmark_list_with_next_cursor(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. size와 동일한 개수의 아이템 조건 준비
    2. get_bookmark_list 호출
    3. next_cursor 생성 및 값 검증
    """
    TEST_USER_ID = uuid.uuid4()
    TEST_PROBLEM_ID = "test123"
    TEST_CHAT_ID = 123
    TEST_DATE_TIME = datetime.now()

    TEST_CHAT_DETAIL = MagicMock(spec=ChatDetail)
    TEST_CHAT_DETAIL.has_active_goal = True

    TEST_PROBLEM = Problem(
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
        correct_answers=[Answer(answer="1", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )

    TEST_CHAT_PROBLEM = ChatProblemWithChatDetailAndWithProblem(
        id=1,
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=True,
        bookmarked_at=TEST_DATE_TIME,
        problem=TEST_PROBLEM,
        chat=TEST_CHAT_DETAIL,
    )

    mock_chat_problem_service.get_bookmarked_problems.return_value = [
        TEST_CHAT_PROBLEM,
        TEST_CHAT_PROBLEM,
    ]

    paginate_filter = CursorPaginateParams(size=2)

    response = await bookmark_use_case.get_bookmark_list(
        user_id=TEST_USER_ID,
        subject=SubjectEnum.MATH,
        status_list=[],
        paginate_filter=paginate_filter,
    )

    assert isinstance(response, CursorPaginateResponse)
    assert len(response.items) == 2
    assert response.next_cursor is not None

    decoded = decode_cursor(response.next_cursor)
    assert decoded.get(ChatProblem.FIELD_BOOKMARKED_AT) == TEST_DATE_TIME.isoformat()


@pytest.mark.asyncio
async def test_get_bookmark_list_with_incoming_cursor(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 인코딩된 커서 조건 준비
    2. get_bookmark_list 호출
    3. 디코딩된 cursor_bookmarked_at 전달 확인
    """
    TEST_USER_ID = uuid.uuid4()
    TEST_PROBLEM_ID = "test123"
    TEST_CHAT_ID = 123
    TEST_DATE_TIME = datetime.now()

    TEST_CHAT_DETAIL = MagicMock(spec=ChatDetail)
    TEST_CHAT_DETAIL.has_active_goal = True

    TEST_PROBLEM = Problem(
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
        correct_answers=[Answer(answer="1", accepted_answers=None)],
        level=ProblemLevel.MEDIUM,
        type=ProblemAnswerType.SINGLE_SHORT_ANSWER,
        semester=1,
    )

    TEST_CHAT_PROBLEM = ChatProblemWithChatDetailAndWithProblem(
        id=1,
        chat_id=TEST_CHAT_ID,
        problem_id=TEST_PROBLEM_ID,
        user_id=TEST_USER_ID,
        number=1,
        status=ProblemStatus.UNSOLVED,
        last_answer=None,
        is_bookmarked=True,
        bookmarked_at=TEST_DATE_TIME,
        problem=TEST_PROBLEM,
        chat=TEST_CHAT_DETAIL,
    )

    incoming_cursor = encode_cursor(
        {ChatProblem.FIELD_BOOKMARKED_AT: TEST_DATE_TIME}
    )

    mock_chat_problem_service.get_bookmarked_problems.return_value = [
        TEST_CHAT_PROBLEM
    ]

    paginate_filter = CursorPaginateParams(
        size=1,
        cursor=incoming_cursor,
    )

    await bookmark_use_case.get_bookmark_list(
        user_id=TEST_USER_ID,
        subject=SubjectEnum.ENGLISH,
        status_list=[],
        paginate_filter=paginate_filter,
    )

    mock_chat_problem_service.get_bookmarked_problems.assert_called_once_with(
        user_id=TEST_USER_ID,
        subject=[SubjectEnum.ENGLISH],
        status=[],
        size=1,
        cursor_bookmarked_at=TEST_DATE_TIME,
    )


@pytest.mark.asyncio
async def test_get_bookmark_list_empty_result(
    bookmark_use_case: ProblemBookmarkUseCase,
    mock_chat_problem_service: AsyncMock,
):
    """
    1. 북마크 결과가 없는 조건 준비
    2. get_bookmark_list 호출
    3. 빈 items 반환 검증
    """
    # 1.
    TEST_USER_ID = uuid.uuid4()

    mock_chat_problem_service.get_bookmarked_problems.return_value = []

    TEST_PAGINATE_FILTER = CursorPaginateParams(size=10)

    # 2.
    response = await bookmark_use_case.get_bookmark_list(
        user_id=TEST_USER_ID,
        subject=None,
        status_list=[],
        paginate_filter=TEST_PAGINATE_FILTER,
    )

    # 3.
    assert isinstance(response, CursorPaginateResponse)
    assert response.items == []
    assert response.next_cursor is None
