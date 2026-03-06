# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any

from common.service.exceptions import BaseAppException


class ChatException(BaseAppException):
    """채팅 관련 예외의 기본 클래스입니다."""
    default_msg = "채팅 오류가 발생했습니다."


class ChatNotFoundException(ChatException):
    """채팅방이 존재하지 않을 때 발생하는 예외"""

    default_msg = "해당 채팅을 찾을 수 없습니다."

    def __init__(self, chat_id: int | None) -> None:

        super().__init__(
            data={
                "chat_id" : chat_id
            }
        )


class ChatAccessForbiddenException(ChatException):
    """채팅방은 존재하나, 요청한 사용자 소유가 아닐 때 발생하는 예외 (403)"""

    default_msg = "해당 채팅방에 대한 접근 권한이 없습니다."

    def __init__(self, chat_id: int | None) -> None:
        super().__init__(data={"chat_id": chat_id})


# 채팅 문제 관련 Exception

class ChatProblemDuplicateException(ChatException):
    default_msg = "채팅에서 문제가 중복되었습니다."
    def __init__(self, problem_id: str) -> None:
        super().__init__(
            data={
                "problem_id" : problem_id
            }
        )

class ChatProblemNotFoundException(ChatException):
    """채팅 문제가 존재하지 않을 때 발생하는 예외"""

    default_msg = "채팅에서 해당 문제를 찾을 수 없습니다."
    def __init__(
        self,
        chat_id: int | None = None,
        problem_id: str | None = None,
        chat_problem_id: int | None = None
    ) -> None:
        exception_data: dict[str, Any] = {}
        if chat_id is not None:
            exception_data["chat_id"] = chat_id

        if problem_id is not None:
            exception_data["problem_id"] = problem_id

        if chat_problem_id is not None:
            exception_data["chat_problem_id"] = chat_problem_id

        super().__init__(
            data=exception_data
        )


class ChatProblemAllProblemRecommendedException(ChatException):
    """채팅에서 추천할 문제가 없을 때 발생"""
    default_msg = "더이상 추천할 문제가 없습니다."


class AlreadySolvedException(ChatException):
    """이미 정답 처리된 문제에 답안을 다시 제출할 때 발생하는 예외"""
    default_msg = "이미 정답 처리된 문제입니다."
    def __init__(self, problem_id: str) -> None:
        super().__init__(
            data={
                "problem_id" : problem_id
            }
        )


class StreamTimeoutException(ChatException):
    default_msg = "모델 응답 스트림 응답이 일정 시간 이내 오지 않았습니다."
