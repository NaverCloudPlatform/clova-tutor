# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from base_repository import BaseMapper
from pydantic import TypeAdapter

from chats.database.models import ChatMessageModel
from chats.domain.chat_message.chat_message import ChatMessage
from chats.domain.chat_message.message_content import ChatMessageContent
from chats.domain.chat_message.metadata import ChatMessageMetadata
from chats.domain.chat_message.system_content import SystemMessageContent


class ChatMessageMapper(BaseMapper):
    def __init__(self) -> None:
        self._md_adapter = TypeAdapter(ChatMessageMetadata)
        self._content_adapter = TypeAdapter(list[ChatMessageContent | SystemMessageContent])

    def to_schema(self, orm_object: ChatMessageModel) -> ChatMessage:
        orm_dict = orm_object.__dict__.copy()
        orm_dict.update({
            ChatMessage.FIELD_CONTENT: self._content_adapter.validate_json(orm_object.content),
            ChatMessage.FIELD_META_DATA: self._md_adapter.validate_json(orm_object.meta_data)
        })
        return ChatMessage.model_validate(orm_dict)

    def to_orm(self, domain_object: ChatMessage) -> ChatMessageModel:
        return ChatMessageModel(
            **domain_object.model_dump(exclude={ChatMessage.FIELD_CONTENT, ChatMessage.FIELD_META_DATA}),
            content=self._content_adapter.dump_json(list(domain_object.content)).decode(),
            meta_data=self._md_adapter.dump_json(domain_object.meta_data).decode()
        )
