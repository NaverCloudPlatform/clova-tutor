# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field
from typing_extensions import Doc

from chats.domain.chat_problem import ProblemStatus
from common.domain.schema import CommonBase
from problems.domain.problem import Problem


class ChatMessageSubType(StrEnum):
    """채팅 메시지의 세부 타입을 정의하는 열거형 클래스입니다.

    Attributes:
        TEXT: 텍스트 메시지
        IMAGES: 이미지 메시지
        PROBLEM_LINK: 문제 링크 메시지
        QUOTE: 인용 메시지 (문제 인용 시)
    """

    TEXT = "text"
    IMAGES = "images"
    PROBLEM_LINK = "problem_link"
    QUOTE = "quote"
    PROBLEM_RECOMMENDED = "problem_recommended"


class ChatMessageQuoteType(StrEnum):
    """채팅 메시지의 인용 타입을 정의하는 열거형 클래스입니다.

    Attributes:
        PROBLEM: 문제 인용
        CHAT: 채팅 인용
    """

    PROBLEM = "problem"
    CHAT = "chat"

# TextContent ------------------

class TextValue(CommonBase):
    text: Annotated[str, Doc("메세지 텍스트")]


class TextContent(CommonBase):
    m_type: Annotated[
        Literal[ChatMessageSubType.TEXT], Doc("텍스트 타입")
    ]
    value: Annotated[TextValue, Doc("텍스트 타입 필드")]

# ProblemLinkContent ------------------

class ProblemLinkValue(CommonBase):
    problem_id: Annotated[str, Doc("문제 ID")]


class ProblemLinkContent(CommonBase):
    m_type: Annotated[
        Literal[ChatMessageSubType.PROBLEM_LINK], Doc("문제 링크 메세지 타입")
    ]
    value: Annotated[ProblemLinkValue, Doc("문제 링크 메세지 값")]

# ImagesContent ------------------

class ImagesValue(CommonBase):
    sources: Annotated[list[str], Doc("이미지 URL")]


class ImagesContent(CommonBase):
    m_type: Annotated[
        Literal[ChatMessageSubType.IMAGES], Doc("이미지 메세지 타입")
    ]
    value: Annotated[ImagesValue, Doc("이미지 메세지 값")]

# QuoteContent ------------------

class ChatQuoteSource(CommonBase):
    # 인용이 problem 인지, chat인지 구분
    type: Annotated[
        Literal[ChatMessageQuoteType.CHAT], Doc("인용 타입")
    ]
    chat_id: Annotated[int, Doc("인용된 채팅 ID")]


class ProblemQuoteSource(CommonBase):
    type: Annotated[
        Literal[ChatMessageQuoteType.PROBLEM], Doc("메시지 텍스트")
    ]
    problem_id: Annotated[str, Doc("인용된 문제 ID")]

class QuoteValue(CommonBase):
    text: Annotated[str, Doc("인용 중 특정 텍스트를 기록합니다.")]
    source: Annotated[
        ProblemQuoteSource | ChatQuoteSource,
        Doc("인용 타입입니다. 채팅과 문제를 인용할 수 있습니다."),
    ]

class QuoteContent(CommonBase):
    m_type: Annotated[
        Literal[ChatMessageSubType.QUOTE], Doc("인용 메세지 타입")
    ]
    value: Annotated[QuoteValue, Doc("인용 메세지 값")]

# ProblemRecommendedContent ------------------

class ProblemRecommendedValue(CommonBase):
    problem_id: Annotated[str, Doc("추천 문제 ID")]
    category: Annotated[str | None, Doc("추천 문제 카테고리")]
    status: Annotated[ProblemStatus, Doc("추천 문제 상태")]


class ProblemRecommendedContent(CommonBase):
    m_type: Annotated[
        Literal[ChatMessageSubType.PROBLEM_RECOMMENDED], Doc("추천 문제 타입")
    ]
    value: Annotated[ProblemRecommendedValue, Doc("추천 문제 값")]



ChatMessageContent = Annotated[
    TextContent
    | ProblemLinkContent
    | ImagesContent
    | QuoteContent
    | ProblemRecommendedContent,
    Field(discriminator="m_type"),
]


def create_image_content(imgs: list[str]) -> ImagesContent:
    image_content = ImagesContent(
        m_type=ChatMessageSubType.IMAGES,
        value=ImagesValue(sources=imgs),
    )
    return image_content


def create_problem_content(problem: Problem, problem_status: ProblemStatus = ProblemStatus.UNSOLVED) -> ProblemRecommendedContent:
    pc = ProblemRecommendedContent(
        m_type=ChatMessageSubType.PROBLEM_RECOMMENDED,
        value=ProblemRecommendedValue(
            problem_id=problem.id,
            category=problem.category,
            status=problem_status
        )
    )
    return pc


def create_text_content(text: str) -> TextContent:
    return TextContent(
        m_type=ChatMessageSubType.TEXT, value=TextValue(text=text)
    )
