# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from chats.service.exceptions import ChatException


class StreamAlreadyInProgressException(ChatException):
    """현재 채팅에 대해 스트리밍 응답이 이미 진행 중일 때 발생하는 예외"""
    default_msg = "현재 이 채팅에 대해 스트리밍 응답이 이미 진행 중입니다."

class StreamAlreadyFinishException(ChatException):
    """현재 채팅에 대해 스트리밍 응답이 이미 진행 중일 때 발생하는 예외"""
    default_msg = "현재 이 채팅에 대해 스트리밍 응답이 이미 끝났습니다."
