# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from datetime import datetime
from typing import Any, cast
from uuid import UUID

from chats.domain.chat import Chat
from chats.domain.chat_problem import ChatProblem, ProblemStatus
from chats.presentation.schemas.request_dto import ProblemBookmarkCreateRequestBody
from chats.presentation.schemas.response_dto import (
    ProblemBookmarkChatProblemResponse,
    ProblemBookmarkChatResponse,
    ProblemBookmarkCheckResponse,
    ProblemBookmarkCreateResponse,
    ProblemBookmarkResponse,
    ProblemDuplicateStatus,
)
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import ChatAccessForbiddenException
from common.presentation.pagination import (
    CursorPaginateParams,
    CursorPaginateResponse,
    decode_cursor,
    encode_cursor,
)
from common.utils.utils import attach_timezone
from problems.domain.problem import SubjectEnum
from problems.presentation.schemas.response_mapper import ProblemResponseMapper


class ProblemBookmarkUseCase:
    def __init__(
        self,
        chat_problem_service: ChatProblemService,
        chat_service: ChatService,
    ) -> None:
        self.chat_problem_service = chat_problem_service
        self.chat_service = chat_service

    async def _validate_chat(self, chat_id: int, user_id: UUID) -> Chat:
        chat = await self.chat_service.get_chat_by_id(chat_id)
        if chat.user_id != user_id:
            raise ChatAccessForbiddenException(chat_id)
        return chat

    async def check_problem_bookmark_duplicate(
        self,
        user_id: UUID,
        problem_id: str
    ) -> ProblemBookmarkCheckResponse:
        duplicated = await self.chat_problem_service.exists_by_problem_id(
            problem_id=problem_id,
            user_id=user_id,
            is_bookmarked=True
        )

        final_status = ProblemDuplicateStatus.UNIQUE
        if duplicated:
            final_status = ProblemDuplicateStatus.DUPLICATE

        return ProblemBookmarkCheckResponse(status=final_status)


    async def get_bookmark_list(
        self,
        user_id: UUID,
        subject: SubjectEnum,
        status_list: list[ProblemStatus],
        paginate_filter: CursorPaginateParams
    ) -> CursorPaginateResponse[ProblemBookmarkResponse]:
        cursor: dict[str, Any] = {}
        if paginate_filter.cursor is not None:
            cursor =  decode_cursor(paginate_filter.cursor)

        cursor_bookmarked_at_str = cast(str | None ,cursor.get(ChatProblem.FIELD_BOOKMARKED_AT, None))
        cursor_bookmarked_at: datetime | None = None
        if cursor_bookmarked_at_str:
            cursor_bookmarked_at = datetime.fromisoformat(cursor_bookmarked_at_str)

        bms = await self.chat_problem_service.get_bookmarked_problems(
            user_id=user_id,
            subject=[subject],
            status=status_list,
            size=paginate_filter.size,
            cursor_bookmarked_at=cursor_bookmarked_at,
        )

        next_cursor: str | None = None
        if len(bms) == paginate_filter.size:
            last_bm = bms[-1]
            next_cursor = encode_cursor({
                ChatProblem.FIELD_BOOKMARKED_AT : last_bm.bookmarked_at
            })

        res: list[ProblemBookmarkResponse] = []
        for bm in bms:
            p = bm.problem
            res.append(
                ProblemBookmarkResponse(
                    bookmarked_at=attach_timezone(cast(datetime, bm.bookmarked_at)),
                    chat=ProblemBookmarkChatResponse(
                        id=bm.chat_id,
                        has_active_goal=bm.chat.has_active_goal
                    ),
                    problem=ProblemBookmarkChatProblemResponse(
                        number=bm.number,
                        status=bm.status,
                        last_answer=bm.last_answer,
                        problem_info=ProblemResponseMapper.to_response(p)
                    )
                )
            )

        return CursorPaginateResponse(
            items=res,
            next_cursor=next_cursor
        )


    async def bookmark_problem(
        self,
        user_id: UUID,
        body: ProblemBookmarkCreateRequestBody
    ) -> ProblemBookmarkCreateResponse:
        chat_id = body.chat_id
        problem_id = body.problem_id

        await self._validate_chat(chat_id, user_id)

        cm = await self.chat_problem_service.update_bookmark(
            chat_id=chat_id,
            problem_id=problem_id,
            user_id=user_id,
            is_bookmarked=body.is_bookmarked,
            bookmarked_at=body.bookmarked_at
        )

        return ProblemBookmarkCreateResponse(
            id=cm.id,
            chat_id=cm.chat_id,
            problem_id=cm.problem_id,
            is_bookmarked=cm.is_bookmarked,
            bookmarked_at=attach_timezone(cm.bookmarked_at) if cm.bookmarked_at else None
        )


