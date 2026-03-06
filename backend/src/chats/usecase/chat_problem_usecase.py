# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from chats.domain.chat import Chat
from chats.domain.chat_problem import ProblemStatus
from chats.presentation.schemas.request_dto import ChatProblemSubmitRequestBody
from chats.presentation.schemas.response_dto import (
    ActiveGoalResponse,
    ChatProblemDetailResponse,
    ChatProblemResponse,
    ChatProblemSubmitResponse,
)
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import (
    AlreadySolvedException,
    ChatAccessForbiddenException,
)
from goals.domain.goal import Goal, GoalStatus
from goals.service.exceptions import NotFoundGoalException
from goals.service.goal_service import GoalService
from problems.presentation.schemas.response_mapper import ProblemResponseMapper
from problems.service.problem_service import ProblemService


class ChatProblemUseCase:
    def __init__(
        self,
        chat_service: ChatService,
        chat_problem_service: ChatProblemService,
        problem_service: ProblemService,
        goal_service: GoalService
    ) -> None:
        self.chat_service = chat_service
        self.chat_problem_service = chat_problem_service
        self.problem_service = problem_service
        self.goal_service = goal_service


    async def _validate_chat(
        self,
        chat_id: int,
        user_id: UUID
    ) -> Chat:
        chat = await self.chat_service.get_chat_by_id(chat_id)
        if chat.user_id != user_id:
            raise ChatAccessForbiddenException(chat_id)
        return chat


    async def get_chat_problems(
        self,
        chat_id: int,
        user_id: UUID
    ) -> list[ChatProblemResponse]:
        """
        1. 채팅방과 유저가 올바른지 판단 합니다.
        2. 주어진 chat_id에 해당하는 chat_problems 를 가져옵니다.
        """

        # 1.
        await self._validate_chat(chat_id, user_id)

        # 2.
        cps = await self.chat_problem_service.get_chat_problems_with_detail(chat_id)

        res: list[ChatProblemResponse] = []
        for cp in cps:
            cpr = ChatProblemResponse(
                id=cp.problem_id,
                number=cp.number,
                status=cp.status,
                category=cp.problem.category,
                grade=cp.problem.grade,
                level=cp.problem.level
            )
            res.append(cpr)
        return res


    async def get_chat_problem(
        self,
        chat_id: int,
        problem_id: str,
        user_id: UUID
    ) -> ChatProblemDetailResponse:
        """
        1. 채팅방과 유저가 올바른지 판단 합니다.
        2. 주어진 문제에 해당하는 chat_problem 을 가져옵니다.
        3. 주어진 problem_id를 바탕으로 문제를 가져옵니다.
        """
        # 1.
        await self._validate_chat(chat_id, user_id)

        # 2.
        cp = await self.chat_problem_service.get_chat_problem(
            chat_id=chat_id, problem_id=problem_id
        )

        # 3.
        p = await self.problem_service.get_problem_by_id(problem_id)

        return ChatProblemDetailResponse(
            number=cp.number,
            status=cp.status,
            last_answer=cp.last_answer,
            is_bookmarked=cp.is_bookmarked,
            problem_info=ProblemResponseMapper.to_response(p)
        )

    def _determine_next_problem_status(
        self,
        current_status: ProblemStatus,
        is_correct: bool,
        problem_id: str
    ) -> ProblemStatus:
        # 1. 이미 정답 처리된 문제에 제출한 경우 예외
        if current_status in [ProblemStatus.CORRECT,ProblemStatus.REVIEWED]:
            raise AlreadySolvedException(problem_id=problem_id)

        # 2. 틀렸을 경우, 바로 틀림 리턴
        if not is_correct:
            return ProblemStatus.WRONG

        # 3. 맞았을 경우에는 다음 고려
        match current_status:
            case ProblemStatus.UNSOLVED:
                return ProblemStatus.CORRECT

            case ProblemStatus.WRONG:
                return ProblemStatus.REVIEWED

            # 기본값 mypy 예외
            case _:
                raise ValueError("해당 ProblemState는 핸들링이 되지 않았습니다.")


    async def submit_answer(
        self,
        chat_id: int,
        problem_id: str,
        req: ChatProblemSubmitRequestBody,
        user_id: UUID
    ) -> ChatProblemSubmitResponse:
        """
        1. 채팅방과 유저가 올바른지 판단 합니다.
        2. 주어진 문제에 해당하는 chat_problem 을 가져옵니다.
        3. 정답을 판단합니다.
        4. 정답 및 이전 상태를 바탕으로 다음 상태를 결정합니다.
        5. 다음 상태로 업데이트 합니다.
        6. 현재 목표 달성 경우를 판단합니다.
        6-1. 있을 경우, 문제 맞힌 수를 증가시킵니다.
        7. 채팅의 최신 사용을 갱신합니다.
        """

        # 1.
        await self._validate_chat(chat_id, user_id)

        # 2.
        cp = await self.chat_problem_service.get_chat_problem(
            chat_id=chat_id,
            problem_id=problem_id
        )

        # 3.
        is_correct = await self.problem_service.submit_problem_answer(
            cp.problem_id, req.answer.answer
        )

        # 4.
        next_status= self._determine_next_problem_status(
            ProblemStatus(cp.status),
            is_correct,
            cp.problem_id
        )

        # 5.
        await self.chat_problem_service.update_chat_problem_status(
            chat_problem_id=cp.id,
            status=next_status,
            last_answer=str(req.answer.answer)
        )

        # 6.
        active_goal: Goal | None = None
        if is_correct:
            try:
                active_goal = await self.goal_service.get_goal_by_chat_id(
                    chat_id=chat_id, status=GoalStatus.ACTIVE
                )
            except NotFoundGoalException:
                pass

        # 6-1.
        if active_goal is not None and active_goal.status == GoalStatus.ACTIVE:
            active_goal = await self.goal_service.update_solved_count(active_goal.id, 1)

        # 7.
        await self.chat_service.update_chat_latest_used_at(chat_id)

        resp = ChatProblemSubmitResponse(
            is_correct=is_correct,
            active_goal=None
        )

        if active_goal:
            resp.active_goal = ActiveGoalResponse(
                id=active_goal.id,
                goal_count=active_goal.goal_count,
                solved_count=active_goal.solved_count
            )

        return resp
