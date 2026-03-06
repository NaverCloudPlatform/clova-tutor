# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from chats.database.models import ChatProblemModel
from chats.database.repository.chat_problem_repository import (
    ChatProblemFilter,
    ChatProblemRepository,
)
from chats.domain.chat_problem import (
    ChatProblem,
    ChatProblemDetail,
    ChatProblemWithChatDetailAndWithProblem,
    ProblemStatus,
)
from chats.service.chat_service import ChatService
from chats.service.exceptions import (
    ChatProblemAllProblemRecommendedException,
    ChatProblemDuplicateException,
    ChatProblemNotFoundException,
)
from common.utils.logger import register_internal_service_log
from problems.domain.problem import Problem, SubjectEnum
from problems.service.problem_service import ProblemService


class ChatProblemService:
    def __init__(
        self,
        chat_problem_repo: ChatProblemRepository,
        chat_service: ChatService,
        problem_service: ProblemService
    ) -> None:
        self.chat_problem_repo = chat_problem_repo
        self.chat_service = chat_service
        self.problem_service = problem_service


    async def exists_by_chat_id(
        self,
        chat_id: int
    ) -> bool:
        return (await self.chat_problem_repo.exists(flt=ChatProblemFilter(chat_id=chat_id)))

    async def exists_by_problem_id(
        self,
        problem_id: str,
        *,
        chat_id: int | None = None,
        user_id: UUID | None = None,
        is_bookmarked: bool | None = None
    ) -> bool:
        return (await self.chat_problem_repo.exists(
            flt=ChatProblemFilter(
                    chat_id=chat_id,
                    problem_id=problem_id,
                    user_id=user_id,
                    is_bookmarked=is_bookmarked
                )
            )
        )

    async def get_bookmarked_problems(
        self,
        user_id: UUID,
        subject: list[SubjectEnum],
        status: list[ProblemStatus],
        *,
        size: int,
        cursor_bookmarked_at: datetime | None  = None,
    ) -> list[ChatProblemWithChatDetailAndWithProblem]:
        return await self.chat_problem_repo.get_bookmarked_problems(
            flt=ChatProblemFilter(
                user_id=user_id,
                status=[s.value for s in status],
                is_bookmarked=True
            ),
            subject_filter=subject,
            cursor_bookmarked_at=cursor_bookmarked_at,
            size=size
        )

    async def add_problem_to_chat(
        self,
        chat_id: int,
        problem_id: str,
        user_id: UUID,
    ) -> ChatProblem:
        # 1. 가장 최신의 number를 받아옴
        latest_cp = await self.chat_problem_repo.get_list(
            size=1,
            flt=ChatProblemFilter(chat_id=chat_id),
            order_by=[ChatProblemModel.created_at.desc(),]
        )

        next_no = 1
        if len(latest_cp) > 0:
            next_no = latest_cp[0].number + 1

        chat_problem = ChatProblem(
            chat_id=chat_id,
            problem_id=problem_id,
            status=ProblemStatus.UNSOLVED,
            user_id=user_id,
            last_answer=None,
            number=next_no,
            is_bookmarked=False,
            bookmarked_at=None
        )
        try:
            created = await self.chat_problem_repo.create(chat_problem)
        except IntegrityError as e:
            register_internal_service_log(f"{e}")
            raise ChatProblemDuplicateException(problem_id=problem_id)

        return created


    async def get_chat_problems(
        self,
        chat_id: int,
    ) -> list[ChatProblem]:
        cps: list[ChatProblem] = await self.chat_problem_repo.get_list(flt=ChatProblemFilter(chat_id=chat_id))
        return cps

    async def get_chat_problem(
        self,
        chat_id: int,
        problem_id: str
    ) -> ChatProblem:
        cp: ChatProblem | None = await self.chat_problem_repo.get(flt=ChatProblemFilter(chat_id=chat_id, problem_id=problem_id))
        if cp is None:
            raise ChatProblemNotFoundException(
                chat_id=chat_id,
                problem_id=problem_id
            )
        return cp


    async def get_chat_problems_with_detail(
        self,
        chat_id: int
    ) -> list[ChatProblemDetail]:
        cps = await self.chat_problem_repo.get_with_problems(
            flt=ChatProblemFilter(chat_id=chat_id)
        )
        return cps


    async def get_chat_problem_detail(
        self,
        chat_id: int,
        problem_id: str
    ) -> ChatProblemDetail:
        cp = await self.get_chat_problem(chat_id,problem_id)

        p = await self.problem_service.get_problem_by_id(problem_id)

        return ChatProblemDetail(
            **cp.model_dump(),
            problem=p
        )

    async def find_not_duplicate_problem(
        self,
        chat_id: int,
    ) -> Problem:
        chat = await self.chat_service.get_chat_by_id(chat_id)

        cps = await self.get_chat_problems(chat_id=chat_id)

        exclude_ids = [cp.problem_id for cp in cps]

        random_problem = await self.problem_service.find_random_problem(
            exclude_ids=exclude_ids,
            subject=chat.subject,
            grade=chat.grade
        )

        if random_problem is None:
            raise ChatProblemAllProblemRecommendedException()

        return random_problem


    async def update_bookmark(
        self,
        chat_id: int,
        problem_id: str,
        user_id: UUID,
        is_bookmarked: bool,
        bookmarked_at: datetime | None
    ) -> ChatProblem:
        cp = await self.chat_problem_repo.get(
            flt=ChatProblemFilter(
                chat_id=chat_id,
                problem_id=problem_id,
                user_id=user_id
            ),
            convert_schema=False
        )

        if cp is None:
            raise ChatProblemNotFoundException(
                chat_id=chat_id,
                problem_id=problem_id
            )

        # 시나리오 1. is_bookmarked = True, bookmarked_at = not None 이면, 그대로 사용
        # 시나리오 2. is_bookmarked 이 True 이면서, bookmarked_at 이 False 이면, 서버의 현재값으로 갱신
        if is_bookmarked and bookmarked_at is None:
            bookmarked_at = datetime.now()
        # 시나리오 3. is_bookmarked 이 False 이면, bookmarked_at 은 None
        if not is_bookmarked:
            bookmarked_at = None

        updated = await self.chat_problem_repo.update_from_model(
            cp,
            update={
                ChatProblem.FIELD_IS_BOOKMARKED : is_bookmarked,
                ChatProblem.FIELD_BOOKMARKED_AT : bookmarked_at
            }
        )
        return updated


    async def update_chat_problem_status(
        self,
        chat_problem_id: int,
        status: ProblemStatus,
        last_answer: str | None,
    ) -> ChatProblem:
        cpm = await self.chat_problem_repo.get(
            flt=ChatProblemFilter(id=chat_problem_id),
            convert_schema=False
        )
        if cpm is None:
            raise ChatProblemNotFoundException(chat_problem_id=chat_problem_id)

        updated = await self.chat_problem_repo.update_from_model(
            cpm,
            update={
                ChatProblem.FIELD_STATUS : status,
                ChatProblem.FIELD_LAST_ANSWER : last_answer
            }
        )
        return updated


    async def delete_chat_problems_by_chat_id(
        self,
        chat_id: int
    ) -> None:
        await self.chat_problem_repo.delete(
            flt=ChatProblemFilter(
                chat_id=chat_id
            )
        )
