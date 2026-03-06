# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio
import logging
import uuid

from collections.abc import AsyncIterator
from datetime import datetime
from enum import StrEnum
from typing import cast
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, TypeAdapter

from chats.domain.assistant.assistant_mapper import AssistantMapper
from chats.domain.assistant.assistant_request import AssistantRequest
from chats.domain.assistant.assistant_response import AssistantResponse
from chats.domain.chat import Chat
from chats.domain.chat_message.chat_message import (
    ChatStreamStatus,
    MessageRole,
    MessageType,
)
from chats.domain.chat_message.message_content import (
    ChatMessageContent,
    create_image_content,
    create_problem_content,
    create_text_content,
)
from chats.domain.chat_message.metadata import ChatMessageMetadata, ReActModelToolType
from chats.domain.chat_message.system_content import DateContent, DateValue, SystemMessageSubType
from chats.domain.chat_message.tool_info_mapper import ModelToolMapper
from chats.presentation.schemas.request_dto import ChatMessageCreateRequestBody
from chats.presentation.schemas.response_dto import (
    ChatMessageDeltaStream,
    ChatMessageEvent,
    ChatMessageResponse,
    ChatMessageStopResponse,
    ChatStreamStatusResponse,
    MessageAuthor,
    MessageListResponse,
    MessageMetadataResponse,
    MessageResponse,
    StopResponseStatusValue,
)
from chats.service.chat_message_service import ChatMessageService
from chats.service.chat_problem_service import ChatProblemService
from chats.service.chat_service import ChatService
from chats.service.exceptions import (
    ChatAccessForbiddenException,
    ChatNotFoundException,
    ChatProblemAllProblemRecommendedException,
    ChatProblemNotFoundException,
)
from chats.service.i_assistant_service import IAssistantService
from chats.service.i_stream_lock_service import IStreamLockService
from chats.service.i_stream_service import IChatStreamService
from chats.usecase.exceptions import StreamAlreadyFinishException, StreamAlreadyInProgressException
from chats.utils.constants import ERROR_TEXT, PROBLEM_ERROR_TEXT, RANDOM_PROBLEM_FOUND_TEXT
from chats.utils.utils import format_sse_event, wrap_stream_with_timeout
from common.infra.mysql.mysql import transactional
from common.utils.logger import register_internal_service_log
from common.utils.utils import attach_timezone
from problems.service.exceptions import ProblemNotFoundException
from users.domain.user import User


class ProblemRecommendStatus(StrEnum):
    ERROR = "ERROR"
    RANDOM_PROBLEM_RECOMMENDED = "RANDOM_PROBLEM_RECOMMENDED"
    PROBLEM_RECOMMENDED = "PROBLEM_RECOMMENDED"
    NORMAL = "NORMAL"


class ProblemUpdateSchema(BaseModel):
    problem_id: str | None = None
    status: ProblemRecommendStatus

class ChatMessageUseCase:
    def __init__(
        self,
        chat_service: ChatService,
        chat_message_service: ChatMessageService,
        chat_problem_service: ChatProblemService,
        stream_lock_service: IStreamLockService,
        assistant_service: IAssistantService,
        chat_stream_service: IChatStreamService
    ):
        self.chat_service = chat_service
        self.chat_message_service = chat_message_service
        self.chat_problem_service = chat_problem_service
        self.stream_lock_service = stream_lock_service
        self.assistant_service = assistant_service
        self.chat_stream_service = chat_stream_service


    async def _validate_chat(
        self,
        chat_id: int,
        user_id: UUID
    ) -> Chat:
        chat = await self.chat_service.get_chat_by_id(chat_id)
        if chat.user_id != user_id:
            raise ChatAccessForbiddenException(chat_id)
        return chat

    def _create_sse_payload(
        self,
        chat_id: int,
        contents: list[ChatMessageContent],
        metadata: ChatMessageMetadata,
    ) -> ChatMessageResponse:
        tmp: list[ChatMessageContent] = [create_text_content("")]
        msg_payload = ChatMessageResponse(
            id=-1,
            chat_id=chat_id,
            created_at=attach_timezone(datetime.now()),
            type=MessageType.CHAT,
            author=MessageAuthor(role=MessageRole.ASSISTANT),
            contents=contents + tmp,
            metadata=MessageMetadataResponse(
                tools=metadata.tools,
                system_hints=metadata.system_hints
            )
        )
        return msg_payload


    async def _ensure_today_header(self, chat_id: int) -> None:
        last_msg = await self.chat_message_service.get_latest_message(chat_id)

        today = datetime.now(ZoneInfo("Asia/Seoul")).date()
        if last_msg is None or last_msg.created_at.date() != today:
            today_str = today.isoformat()
            await self.chat_message_service.create_system_message(
                chat_id,
                contents=[DateContent(
                    m_type=SystemMessageSubType.DATE,
                    value=DateValue(text=today_str),
                )]
            )

    async def _problem_update(
        self,
        chat_id: int,
        user_id: UUID,
        state: AssistantResponse,
    ) -> ProblemUpdateSchema:

        recommendation = state.recommendation

        recommended_p_id = recommendation.recommended_problem_id

        if (recommended_p_id == ""
            or await self.chat_problem_service.exists_by_problem_id(problem_id=recommended_p_id, chat_id=chat_id)
        ):
            register_internal_service_log(f"중복 문제 발견 문제 ID: {recommended_p_id}. 랜덤 문제 찾기 로직 수행")
            try:
                p = await self.chat_problem_service.find_not_duplicate_problem(
                    chat_id=chat_id
                )
            except (ChatProblemAllProblemRecommendedException, ChatNotFoundException):
                register_internal_service_log("랜덤 문제 추천 불가 (더 이상 추천할 문제가 없음)")
                return ProblemUpdateSchema(
                    status=ProblemRecommendStatus.ERROR
                )

            await self.chat_problem_service.add_problem_to_chat(chat_id, p.id, user_id)
            return ProblemUpdateSchema(
                    status=ProblemRecommendStatus.RANDOM_PROBLEM_RECOMMENDED,
                    problem_id=p.id
                )
        register_internal_service_log(f"새로운 문제 발견 : {recommended_p_id}")
        await self.chat_problem_service.add_problem_to_chat(chat_id, recommended_p_id, user_id)
        return ProblemUpdateSchema(
            status=ProblemRecommendStatus.PROBLEM_RECOMMENDED,
            problem_id=recommended_p_id
        )

    async def get_chat_status(
        self,
        chat_id: int,
        user_id: UUID
    ) -> ChatStreamStatusResponse:
        await self._validate_chat(chat_id, user_id)
        status = await self.stream_lock_service.check_status(chat_id,None)
        return ChatStreamStatusResponse(
            status=status.status
        )


    async def get_chat_messages(
        self,
        chat_id: int,
        user_id: UUID
    ) -> MessageListResponse:
        await self._validate_chat(chat_id, user_id)

        messages = await self.chat_message_service.get_chat_messages(chat_id)

        res: list[MessageResponse] = []
        for msg in messages:
            payload = {
                "id": msg.id,
                "chat_id": msg.chat_id,
                "created_at": attach_timezone(msg.created_at),
                "type": msg.type,
                "author": {
                    "role": msg.role,
                },
                "contents": msg.content,
                "metadata": MessageMetadataResponse(
                    tools=msg.meta_data.tools,
                    system_hints=msg.meta_data.system_hints
                )
            }

            item: MessageResponse = TypeAdapter(MessageResponse).validate_python(payload)
            res.append(item)
        return MessageListResponse(
            data=res
        )

    @transactional(force_new=True)
    async def _internal_producer_task(
        self,
        req: AssistantRequest,
        user_id: UUID,
        chat_id: int,
        *,
        # Call By Reference 로 에러 발생 시에도, 해당 값 사용
        contents: list[ChatMessageContent],
        metadata: ChatMessageMetadata
    ) -> None:
        """
        1. 모델 응답 streamer 획득 및 timeout 래핑
        2. 매 5번의 발화마다 발화 중지 되었는지 체크
        3. 처음 메시지일 경우 payload 만들어서 전달
        4. 마지막 메시지일 경우 비즈니스 로직 시작
        4-1. 문제 중복 로직 판단 및 추가
        4-2. 중복 로직에 따라 응답 덮어쓰기
        5. 실시간 메시지 청크 전송
        6. 예외 로직 처리
        6-1. 정지 예외 시, DB 저장 X -> 이미 API 에서 저장함
        6-2. 이외의 에러 시, 이전까지의 청크 저장
        7. 최종 DB 저장
        """
        is_first = True
        fragments: list[str] = []

        # 1.
        streamer = self.assistant_service.get_model_stream_response(req)
        streamer_with_timeout: AsyncIterator[AssistantResponse] = wrap_stream_with_timeout(streamer,timeout_seconds=150)

        seq_no = 0
        req_id = str(req.request_id)

        need_to_check_status = True
        need_to_content_collect = True

        has_reference_image = False
        has_recommend_problem = False
        buffered_text = ""

        try:
            async for msg in streamer_with_timeout:
                # 2.
                # 5번의 발화마다 현재 발화가 중지되었는지 체크함
                if seq_no % 5 == 0:
                    status = await self.stream_lock_service.check_status(
                        chat_id=chat_id,
                        request_id=req_id
                    )
                    if status.status == ChatStreamStatus.COMPLETE:
                        raise StreamAlreadyFinishException()
                seq_no += 1

                # 업데이트 되는 metadata 저장
                tool_info = ModelToolMapper.resolve_tools(msg.presentations)
                metadata.tools = tool_info

                # 이미지 데이터 내려올 시 추가 (1회성)
                if has_reference_image is False and msg.reference_image_document:
                    image_content = create_image_content(msg.reference_image_document)
                    contents.append(image_content)
                    has_reference_image = True

                # 3.
                if is_first:
                    has_recommend_problem = any(t.name == ReActModelToolType.RECOMMEND_PROBLEM for t in tool_info)

                    payload = self._create_sse_payload(chat_id,contents, metadata)
                    await self.chat_stream_service.add_stream_message(
                        chat_id=chat_id,
                        conversation_id=req_id,
                        contents=payload.model_dump_json(),
                        is_finish=False
                    )
                    is_first = False

                # 4.
                if msg.finish:
                    need_to_content_collect = False
                    # 4-1. 중복 판단 로직
                    # 모델의 문제 추천 응답 로직 -> stream 여부로 판단 가능
                    def _is_stream_response(cur_frag: list[str]) -> bool:
                        # FYI : 문제 추천 응답 시에는 스트림 응답이 아닙니다.
                        return len(cur_frag) > 10

                    has_recommend_problem = any(t.name == ReActModelToolType.RECOMMEND_PROBLEM for t in tool_info)

                    updated = ProblemUpdateSchema(status=ProblemRecommendStatus.NORMAL)
                    if has_recommend_problem and not _is_stream_response(fragments):
                        updated = await self._problem_update(chat_id, user_id, msg)

                    need_error = False
                    if updated.status in [ProblemRecommendStatus.RANDOM_PROBLEM_RECOMMENDED, ProblemRecommendStatus.PROBLEM_RECOMMENDED] and updated.problem_id:
                        try:
                            p = await self.chat_problem_service.get_chat_problem_detail(chat_id, updated.problem_id)
                        except (ProblemNotFoundException, ChatProblemNotFoundException):
                            need_error = True
                            updated.status = ProblemRecommendStatus.ERROR

                        if not need_error:
                            p_content = create_problem_content(p.problem)
                            contents.append(p_content)

                    full_text = ""
                    match updated.status:
                        case ProblemRecommendStatus.ERROR:
                            full_text = PROBLEM_ERROR_TEXT
                        case ProblemRecommendStatus.RANDOM_PROBLEM_RECOMMENDED:
                            full_text = RANDOM_PROBLEM_FOUND_TEXT
                        case ProblemRecommendStatus.PROBLEM_RECOMMENDED | ProblemRecommendStatus.NORMAL:
                            full_text = "".join(fragments)
                    contents.append(create_text_content(full_text))
                    break

                # 5.
                fragments.append(msg.model_response)

                delta_text = msg.model_response if msg.model_response else ""
                # 버퍼링
                if has_recommend_problem:
                    if seq_no < 3:
                        buffered_text += delta_text
                        continue

                    elif seq_no == 3:
                        delta_text = buffered_text + delta_text
                        buffered_text = ""

                delta_payload = ChatMessageDeltaStream(text=delta_text)
                await self.chat_stream_service.add_stream_message(
                    chat_id=chat_id,
                    conversation_id=req_id,
                    contents=delta_payload.model_dump_json(),
                    is_finish=False
                )
        # 6.
        except StreamAlreadyFinishException:
            # 이미 종료된 스트림 예외 시 DB 저장 로직 없이 raise
            need_to_check_status = False
            raise
        # 타임아웃 및 그냥 알 수 없는 예외 발생 시 마지막 발화된 내용까지 저장은 함
        except TimeoutError:
            ...
        except Exception as e:
            register_internal_service_log(f"비동기 스트림 테스크에서 에러 발생 : {e}", level=logging.ERROR)
        finally:
            # message_end 지점까지 호출 실패 시, 최종 수행
            if need_to_content_collect:
                if len(fragments) == 0 and need_to_check_status:
                    contents.append(create_text_content(ERROR_TEXT))
                else:
                    contents.append(create_text_content("".join(fragments)))

        # 7.
        if need_to_check_status:
            # 다시 한 번 체크
            status = await self.stream_lock_service.check_status(chat_id,req_id)
            # 트랜잭션의 롤백을 유도함 / 따라서, 채팅 문제가 저장이 되지 않게 해야함
            if status.status == ChatStreamStatus.COMPLETE:
                raise StreamAlreadyFinishException()

            await self.chat_message_service.create_assistant_message(
                chat_id=chat_id,
                contents=contents,
                metadata=metadata
            )


    async def _stream_producer_task(
        self,
        req: AssistantRequest,
        user_id: UUID,
        chat_id: int,
        chat_stream_channel: asyncio.Queue[bool]
    ) -> None:
        """
        1. 스트림 락 획득
        2. 내부적으로 채팅 스트림 로직 수행
        3. 최종적으로 마지막 메시지 저장
        4. 스트림 메시지 삭제 로직 수행
        """

        req_id = str(req.request_id)
        # 1.
        async with self.stream_lock_service.acquire_lock(chat_id, req_id) as acquired:
            chat_stream_channel.put_nowait(acquired)
            if not acquired:
                return

            register_internal_service_log(
                f"REDIS LOCK ACQUIRED : {req_id}"
            )

            contents: list[ChatMessageContent] = []
            metadata = ChatMessageMetadata()

            try:
                # 2.
                await self._internal_producer_task(
                    req=req,
                    user_id=user_id,
                    chat_id=chat_id,
                    contents=contents,
                    metadata=metadata
                )
            except Exception:
                ...

            # 3.
            await self.chat_stream_service.add_stream_message(
                chat_id=chat_id,
                conversation_id=req_id,
                contents=self._create_sse_payload(chat_id, contents, metadata).model_dump_json(),
                is_finish=True
            )

        # 4.
        # 이전의 스트림은 지움. 이미 DB에 저장되어 있기 때문에
        try:
            await self.chat_stream_service.delete_stream_message(
                chat_id=chat_id,
                conversation_id=req_id,
                wait_time=1
            )
        except Exception as e:
            register_internal_service_log(
                f"[WARN] Failed to delete Redis stream {chat_id} / {req_id}: {e}",
                level=logging.WARN
            )


    async def _stream_consumer_task(
        self,
        chat_id: int,
        conversation_id: str
    ) -> AsyncIterator[str]:
        streamer = self.chat_stream_service.stream_read_messages(
            chat_id=chat_id,
            conversation_id=conversation_id,
        )

        try:
            async for msg in wrap_stream_with_timeout(streamer, timeout_seconds=60):
                if msg.is_finish:
                    yield format_sse_event(str(ChatMessageEvent.MESSAGE_END), msg.content.model_dump_json(ensure_ascii=False))
                    break

                if msg.seq == 1:
                    yield format_sse_event(str(ChatMessageEvent.MESSAGE_START), msg.content.model_dump_json(ensure_ascii=False))
                    continue

                yield format_sse_event(str(ChatMessageEvent.MESSAGE_DELTA), msg.content.model_dump_json(ensure_ascii=False))
        except TimeoutError:
            return

    async def stream_message(
        self,
        chat_id: int,
        req: ChatMessageCreateRequestBody,
        user: User
    ) -> AsyncIterator[str]:
        """
        1. 채팅방과 유저 Id 확인
        2. 모델 서버와 통신을 위한 request 생성
        3. 비동기 테스크로 모델 응답 스트림 생성
        4. 해당 비동기에서 확실하게 채팅 상태 잠금 확인
        5. 날짜 변경 메시지 작성
        6. 유저 입력 DB 저장
        7. 첫 대화일 시, 채팅방 제목 생성 로직 수행
        8. SSE 스트림 응답 테스크 반환
        """
        # 1.
        chat = await self._validate_chat(chat_id, user.id)

        request_id = uuid.uuid4()

        # 2.
        assistant_req = AssistantMapper.build_assistant_request(
            request_id=request_id,
            chat_id=chat_id,
            subject=chat.subject,
            grade=chat.grade,
            user_id=user.id,
            user_name=user.name,
            contents=req.contents,
            metadata=ChatMessageMetadata(
                system_hints=req.metadata.system_hints
            )
        )
        register_internal_service_log(f"BE Server Request : {assistant_req}")

        chat_stream_channel = asyncio.Queue[bool](maxsize=1)
        # 3.
        asyncio.create_task(self._stream_producer_task(
            req= assistant_req,
            user_id=user.id,
            chat_id=chat_id,
            chat_stream_channel=chat_stream_channel
        ))

        # 4.
        lock_status = await chat_stream_channel.get()
        if not lock_status:
            raise StreamAlreadyInProgressException()

        # 5.
        await self._ensure_today_header(chat_id)

        # 6.
        await self.chat_message_service.create_user_message(
            chat_id=chat_id,
            contents=req.contents,
            metadata=ChatMessageMetadata(
                tools=[],
                problem_recommended=None,
                system_hints=req.metadata.system_hints
            )
        )

        # 7.
        # 제목 업데이트 로직 수행
        has_first_message = await self.chat_message_service.exists_by_chat_id(
            chat_id=chat_id,
            role=[MessageRole.ASSISTANT]
        )
        if not has_first_message:
            chat_title = await self.assistant_service.create_chat_title(
                request=assistant_req.user_query
            )
            # 최대 제목 길이
            chat_title = chat_title[:100]
            await self.chat_service.update_chat_title(
                chat_id=chat_id,
                title=chat_title
            )

        # 8.
        return self._stream_consumer_task(chat_id, str(request_id))

    async def resume(
        self,
        chat_id: int,
        user_id: UUID
    ) -> AsyncIterator[str]:
        await self._validate_chat(chat_id, user_id)
        c_status = await self.stream_lock_service.check_status(
            chat_id=chat_id,
            request_id=None)

        if c_status.status != ChatStreamStatus.IS_STREAMING:
            raise StreamAlreadyFinishException()


        return self._stream_consumer_task(chat_id, cast(str,c_status.stream_id))


    async def stop_stream(
        self,
        chat_id: int,
        user_id: UUID
    ) -> ChatMessageStopResponse:
        await self._validate_chat(chat_id, user_id)

        c_status = await self.stream_lock_service.check_status(chat_id, None)
        if c_status.status == ChatStreamStatus.COMPLETE:
            raise StreamAlreadyFinishException()

        messages = await self.chat_stream_service.read_all_messages_from_stream(
            chat_id=chat_id,
            conversation_id=cast(str, c_status.stream_id),
            offset="0-0"
        )

        full_text = ""
        contents: list[ChatMessageContent] = []
        metadata = ChatMessageMetadata()
        for msg in messages:
            if isinstance(msg.content, ChatMessageDeltaStream):
                full_text += msg.content.text

            elif isinstance(msg.content, ChatMessageResponse):
                msg_content = msg.content
                metadata = ChatMessageMetadata(
                    tools=msg_content.metadata.tools,
                    system_hints=msg_content.metadata.system_hints
                )

        content = create_text_content(full_text)
        contents.append(content)

        await self.chat_message_service.create_assistant_message(
            chat_id,
            contents=contents,
            metadata=metadata
        )
        await self.stream_lock_service.release_lock(chat_id)

        return ChatMessageStopResponse(
            status=StopResponseStatusValue.OK
        )
