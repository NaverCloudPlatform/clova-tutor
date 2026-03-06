# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import Depends

from chats.database.repository.chat_message_repository import ChatMessageRepository
from chats.database.repository.chat_problem_repository import ChatProblemRepository
from chats.database.repository.chat_repository import ChatRepository
from chats.infra.assistant.grpc_assistant_service import get_grpc_assistant_service
from chats.infra.redis.redis_lock_service import get_redis_lock_service
from chats.infra.redis.redis_stream_service import get_redis_stream_service
from chats.service.chat_message_service import ChatMessageService
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.i_assistant_service import IAssistantService
from chats.service.i_stream_lock_service import IStreamLockService
from chats.service.i_stream_service import IChatStreamService
from chats.usecase.chat_message_usecase import ChatMessageUseCase
from chats.usecase.chat_problem_usecase import ChatProblemUseCase
from chats.usecase.chat_usecase import ChatUseCase
from chats.usecase.problem_bookmark_usecase import ProblemBookmarkUseCase
from goals.dependencies import get_goal_service
from goals.service.goal_service import GoalService
from problems.dependencies import get_problem_service
from problems.service.problem_service import ProblemService


async def get_chat_repository() -> ChatRepository:
    return ChatRepository()

async def get_chat_problem_repository(
) -> ChatProblemRepository:
    return ChatProblemRepository()

async def get_chat_message_repository(
) -> ChatMessageRepository:
    return ChatMessageRepository()

# -------------------------------------------------------

async def get_chat_service(
    chat_repo: ChatRepository = Depends(get_chat_repository)
) -> ChatService:
    return ChatService(
        chat_repo=chat_repo
    )


async def get_chat_problem_service(
    chat_problem_repo: ChatProblemRepository = Depends(get_chat_problem_repository),
    chat_service: ChatService = Depends(get_chat_service),
    problem_service: ProblemService = Depends(get_problem_service)
) -> ChatProblemService:
    return ChatProblemService(
        chat_problem_repo=chat_problem_repo,
        chat_service=chat_service,
        problem_service=problem_service
    )


async def get_chat_message_service(
    chat_service: ChatService = Depends(get_chat_service),
    chat_message_repo: ChatMessageRepository = Depends(get_chat_message_repository),
    chat_stream_service: IChatStreamService = Depends(get_redis_stream_service)
) -> ChatMessageService:
    return ChatMessageService(
        chat_service=chat_service,
        chat_message_repo=chat_message_repo,
    )

# -------------------------------------------------------

async def get_chat_usecase(
    chat_service: ChatService = Depends(get_chat_service),
    chat_problem_service: ChatProblemService = Depends(get_chat_problem_service),
    goal_service: GoalService = Depends(get_goal_service),
) -> ChatUseCase:
    return ChatUseCase(
        chat_service=chat_service,
        chat_problem_service=chat_problem_service,
        goal_service=goal_service,
    )


async def get_chat_problem_usecase(
    chat_service: ChatService = Depends(get_chat_service),
    chat_problem_service: ChatProblemService = Depends(get_chat_problem_service),
    problem_service: ProblemService = Depends(get_problem_service),
    goal_service: GoalService = Depends(get_goal_service),
) -> ChatProblemUseCase:
    return ChatProblemUseCase(
        chat_service=chat_service,
        chat_problem_service=chat_problem_service,
        problem_service=problem_service,
        goal_service=goal_service,
    )


async def get_chat_message_usecase(
    chat_service: ChatService = Depends(get_chat_service),
    chat_message_service: ChatMessageService = Depends(get_chat_message_service),
    chat_problem_service: ChatProblemService = Depends(get_chat_problem_service),
    stream_lock_service: IStreamLockService = Depends(get_redis_lock_service),
    assistant_service: IAssistantService = Depends(get_grpc_assistant_service),
    chat_stream_service: IChatStreamService = Depends(get_redis_stream_service)
) -> ChatMessageUseCase:
    return ChatMessageUseCase(
        chat_service=chat_service,
        chat_message_service=chat_message_service,
        chat_problem_service=chat_problem_service,
        stream_lock_service=stream_lock_service,
        assistant_service=assistant_service,
        chat_stream_service=chat_stream_service
    )

async def get_problem_bookmark_usecase(
    chat_problem_service: ChatProblemService = Depends(get_chat_problem_service),
    chat_service: ChatService = Depends(get_chat_service),
) -> ProblemBookmarkUseCase:
    return ProblemBookmarkUseCase(
        chat_problem_service=chat_problem_service,
        chat_service=chat_service,
    )
