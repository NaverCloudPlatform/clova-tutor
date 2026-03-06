# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from chats.domain.assistant.assistant_response import PresentationOption
from chats.domain.chat_message.metadata import (
    ReActModelToolType,
    ToolInfo,
    ToolValueDict,
)


class ModelToolMapper:
    @staticmethod
    def _resolve_tool_name(tool_name: str) -> ReActModelToolType:
        try:
            val: ReActModelToolType = ReActModelToolType(tool_name)
            return val
        except ValueError as e:
            raise ValueError(f"맞는 {tool_name} 이 없습니다.") from e

    @staticmethod
    def resolve_tools(
        presentations:list[PresentationOption]
    ) -> list[ToolInfo]:
        tools: list[ToolInfo] = []
        for pres in presentations:
            tool_name = ModelToolMapper._resolve_tool_name(pres.response_style)
            tool_value: ToolValueDict = {}

            if pres.has_translation_response is not None:
                # 직독직해 응답이 왔으므로 버튼 노출 X
                if pres.has_translation_response:
                    tool_value["translation_button_visible"] = False

            tools.append(ToolInfo(name=tool_name, value=tool_value))

        return tools
