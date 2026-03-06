# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import StreamingResponse

from auths.dependencies import get_current_user, get_current_user_id
from chats.dependencies import get_chat_message_usecase, get_chat_problem_usecase, get_chat_usecase
from chats.presentation.schemas.request_dto import (
    ChatCreateRequestBody,
    ChatMessageCreateRequestBody,
    ChatProblemSubmitRequestBody,
    ChatTitleUpdateRequestBody,
)
from chats.presentation.schemas.response_dto import (
    ChatDetailResponse,
    ChatMessageStopResponse,
    ChatProblemDetailResponse,
    ChatProblemResponse,
    ChatProblemSubmitResponse,
    ChatResponse,
    ChatStreamStatusResponse,
    MessageListResponse,
)
from chats.usecase.chat_message_usecase import ChatMessageUseCase
from chats.usecase.chat_problem_usecase import ChatProblemUseCase
from chats.usecase.chat_usecase import ChatUseCase
from chats.utils.constants import SWAGGER_EXAMPLE_SSE
from common.presentation.pagination import CursorPaginateParams, CursorPaginateResponse
from common.presentation.response import ErrorResponse
from problems.domain.problem import SubjectEnum
from users.domain.user import User

router = APIRouter()


@router.get(
    "",
    response_model=CursorPaginateResponse[ChatResponse],
    description="모든 채팅 목록을 반환합니다.",
)
async def get_chats(
    # 쿼리 파라미터
    cursor_param: CursorPaginateParams = Depends(),
    subject: list[SubjectEnum] | None = Query(None),
    # 의존성 주입
    usecase: ChatUseCase = Depends(get_chat_usecase),
    user_id: UUID = Depends(get_current_user_id),
) -> CursorPaginateResponse[ChatResponse]:
    """현재 사용자의 모든 채팅 목록을 조회합니다.

    Args:
        subject (list[SubjectEnum] | None): 필터링할 과목 목록 (선택적) 없으면 전체 반환
        service (ChatService): 채팅 서비스 객체
        user_id (UUID): 현재 사용자의 ID

    Returns:
        List[ChatResponse]: 채팅 목록
    """
    return (
        await usecase.get_chat_list(
            user_id,
            subject,
            paginate_filter=cursor_param
        )
    )


@router.post(
    "",
    response_model=ChatResponse,
    description="새로운 채팅을 생성합니다.",
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    # Body
    body: ChatCreateRequestBody,
    # 의존성
    usecase: ChatUseCase = Depends(get_chat_usecase),
    user_id: UUID = Depends(get_current_user_id),
) -> ChatResponse:
    """새로운 채팅을 생성합니다.

    Args:
        chat (ChatCreateRequest): 채팅 생성 요청 데이터
        service (ChatService): 채팅 서비스 객체
        user (UserDto): 현재 사용자 정보

    Returns:
        ChatResponse: 생성된 채팅 정보
    """
    return await usecase.create_chat(body, user_id)


@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
    description="특정 채팅의 정보를 반환합니다.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "해당 채팅이 존재하지 않을 경우 반환됩니다.",
        },
    },
)
async def get_chat(
    # Path 파라미터
    chat_id: int,
    # 의존성
    usecase: ChatUseCase = Depends(get_chat_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ChatDetailResponse:
    """특정 채팅의 상세 정보를 조회합니다.

    Args:
        service (ChatDetailService): 채팅 상세 서비스 객체

    Returns:
        ChatResponse: 채팅 상세 정보

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
    """
    return await usecase.get_chat_detail(chat_id, user_id)


@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
    description="특정 채팅의 제목을 수정합니다.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "해당 채팅이 존재하지 않을 경우 반환됩니다.",
        },
    },
)
async def update_chat_title(
    # Path 파라미터
    chat_id: int,
    # Body 파라미터
    chat_update: ChatTitleUpdateRequestBody,
    # 의존성 주입
    usecase: ChatUseCase = Depends(get_chat_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ChatResponse:
    """특정 채팅의 제목을 수정합니다.

    Args:
        chat_update (ChatTitleUpdateRequest): 제목 수정 요청 DTO
        service (ChatDetailService): 채팅 상세 서비스 객체

    Returns:
        ChatResponse: 수정된 채팅 정보

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
    """
    return await usecase.update_title(chat_id, chat_update, user_id)


@router.delete(
    "/{chat_id}",
    description="특정 채팅을 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "해당 채팅이 존재하지 않을 경우 반환됩니다.",
        },
    },
)
async def delete_chat(
    # Path 파라미터
    chat_id: int,
    # 의존성 주입
    usecase: ChatUseCase = Depends(get_chat_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> Response:
    """특정 채팅을 삭제합니다.

    Args:
        service (ChatDetailService): 채팅 상세 서비스 객체

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
    """
    await usecase.delete_chat(chat_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{chat_id}/stream-status",
    response_model=ChatStreamStatusResponse,
    description="현재 채팅방의 스트림 상태를 확인합니다.",
)
async def get_chat_stream_status(
    # Path 파라미터
    chat_id: int,
    # 의존성
    usecase: ChatMessageUseCase = Depends(get_chat_message_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ChatStreamStatusResponse:
    return await usecase.get_chat_status(chat_id, user_id)


@router.post(
    "/{chat_id}/resume",
    response_class=StreamingResponse,
    description="중단된 채팅 스트림을 재개합니다.",
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "example": SWAGGER_EXAMPLE_SSE,
                    }
                }
            },
            "description": "SSE 이벤트 메시지 스트림",
        },
        404: {
            "model": ErrorResponse,
            "description": "해당 채팅이 존재하지 않을 경우 반환됩니다.",
        },
    },
)
async def resume_chat_stream(
    # Path 파라미터
    chat_id: int,
    # 의존성
    usecase: ChatMessageUseCase = Depends(get_chat_message_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> StreamingResponse:
    resume_streamer = await usecase.resume(chat_id, user_id)
    return StreamingResponse(resume_streamer, media_type="text/event-stream")


@router.post(
    "/{chat_id}/stop-conversation",
    description="현재 스트리밍 중인 대화를 중지합니다.",
    response_model=ChatMessageStopResponse
)
async def stop_stream(
    # Path 파라미터
    chat_id: int,
    # 의존성
    usecase: ChatMessageUseCase = Depends(get_chat_message_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ChatMessageStopResponse:
    return await usecase.stop_stream(chat_id, user_id)


@router.get(
    "/{chat_id}/messages",
    response_model=MessageListResponse,
    description="특정 채팅의 메시지 목록을 반환합니다.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "해당 채팅이 존재하지 않을 경우 반환됩니다.",
        },
    },
)
async def get_messages(
    # Path 파라미터
    chat_id: int,
    # 의존성
    usecase: ChatMessageUseCase = Depends(get_chat_message_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> MessageListResponse:
    """특정 채팅의 메시지 목록을 조회합니다.

    Args:
        service (ChatMessageService): 채팅 메시지 서비스 객체

    Returns:
        MessagesListResponse: 메시지 목록

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
    """
    return await usecase.get_chat_messages(chat_id, user_id)


@router.post(
    "/{chat_id}/messages",
    response_class=StreamingResponse,
    description="특정 채팅에 메세지를 전송합니다.",
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "example": SWAGGER_EXAMPLE_SSE,
                    }
                }
            },
            "description": "SSE 이벤트 메시지 스트림",
        },
        404: {
            "model": ErrorResponse,
            "description": "해당 채팅이 존재하지 않을 경우 반환됩니다.",
        },
    },
)
async def send_message(
    #Path 파라미터
    chat_id: int,
    # Body
    body: ChatMessageCreateRequestBody,
    # 의존성
    usecase: ChatMessageUseCase = Depends(get_chat_message_usecase),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """특정 채팅에 메시지를 전송하고 AI 응답을 스트리밍으로 반환합니다.

    Args:
        message (MessageCreateRequest): 메시지 생성 요청 데이터
        service (ChatMessageService): 채팅 메시지 서비스 객체
        user (UserDto): 현재 사용자 정보

    Returns:
        StreamingResponse: SSE 형식의 AI 응답 스트림

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
    """
    # message_generator = await service.create_message(message, user)
    message_generator = await usecase.stream_message(chat_id=chat_id,req=body, user=user)
    return StreamingResponse(message_generator, media_type="text/event-stream")


@router.get(
    "/{chat_id}/problems",
    response_model=list[ChatProblemResponse],
    responses={
        403: {"model": ErrorResponse, "description": "해당 채팅방에 대한 접근 권한이 없는 경우"},
        404: {"model": ErrorResponse, "description": "해당 채팅을 찾을 수 없는 경우"},
    },
)
async def get_chat_problems(
    # Path 파라미터
    chat_id: int,
    # 의존성 주입
    usecase: ChatProblemUseCase = Depends(get_chat_problem_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> list[ChatProblemResponse]:
    """특정 채팅의 문제 목록을 조회합니다.

    Args:
        service (ChatProblemService): 채팅 문제 서비스 객체

    Returns:
        List[ChatProblemResponse]: 채팅 문제 목록

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
    """
    return await usecase.get_chat_problems(chat_id, user_id)


@router.get(
    "/{chat_id}/problems/{problem_id}",
    response_model=ChatProblemDetailResponse,
    responses={
        403: {"model": ErrorResponse, "description": "해당 채팅방에 대한 접근 권한이 없는 경우"},
        404: {
            "model": ErrorResponse,
            "description": "해당 채팅을 찾을 수 없거나, 채팅에서 해당 문제를 찾을 수 없는 경우",
        },
    },
)
async def get_chat_problem(
    # Path 파라미터
    chat_id: int,
    problem_id: str,
    # 의존성 주입
    usecase: ChatProblemUseCase = Depends(get_chat_problem_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ChatProblemDetailResponse:
    """특정 채팅의 특정 문제 상세 정보를 조회합니다.

    Args:
        service (ChatProblemService): 채팅 문제 서비스 객체
        problem_id (int): 문제 ID

    Returns:
        ChatProblemDetailResponse: 문제 상세 정보

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
        ChatProblemNotFoundException: 문제를 찾을 수 없는 경우
    """
    return await usecase.get_chat_problem(chat_id,problem_id,user_id)


@router.post(
    "/{chat_id}/problems/{problem_id}/submit",
    response_model=ChatProblemSubmitResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "이미 정답/복습 처리된 문제에 답안을 다시 제출할 때 반환됩니다.",
        },
    },
)
async def submit_chat_problem(
    # Path 파라미터
    chat_id: int,
    problem_id: str,
    # Body
    body: ChatProblemSubmitRequestBody,
    # 의존성 주입
    usecase: ChatProblemUseCase = Depends(get_chat_problem_usecase),
    user_id: UUID = Depends(get_current_user_id)
) -> ChatProblemSubmitResponse:
    """특정 채팅의 특정 문제에 대한 답안을 제출합니다.

    Args:
        problem_id (int): 문제 ID
        submit (ChatProblemSubmitRequest): 답안 제출 요청 데이터
        service (ChatProblemService): 채팅 문제 서비스 객체

    Returns:
        ChatProblemSubmitResponse: 답안 제출 결과

    Raises:
        ChatNotFoundException: 채팅을 찾을 수 없는 경우
        ChatProblemNotFoundException: 문제를 찾을 수 없는 경우
        AlreadySolvedException: 이미 해결된 문제인 경우
    """
    return await usecase.submit_answer(chat_id,problem_id,body, user_id)
