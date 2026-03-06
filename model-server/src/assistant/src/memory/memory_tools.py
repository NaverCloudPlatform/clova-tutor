# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Literal

from langchain_core.output_parsers import JsonOutputKeyToolsParser
from langchain_core.tools import tool

from assistant.src.utils.load_utils import load_default_prompt


class MemoryTool:
    def __init__(self, llm):
        self.llm = llm
        self.evolution_prompt = load_default_prompt("memory")["evolution_prompt"]

    @tool
    def evolution_memory(
        self,
        should_evolve: bool,
        actions: list[Literal["strengthen", "update_neighbor"]],
        suggested_connections: list[str],
        new_context_neighborhood: list[str],
    ):
        """이 함수는 new memory의 정보를 사용자가 제공했을 때 호출됩니다.

        새로운 memory를 keywords와 context, 그리고 해당 메모리의 The nearest neighbors memories들과 함께 분석하세요.
        이를 바탕으로 아래와 같이 memory evolution와 관련된 의사결정을 내리십시오.

        아래 정보를 바탕으로 다음을 판단하십시오:
            1.	이 메모리를 evolve 해야할 지 결정하세요. (다른 메모리들과의 관계를 고려하세요.)
            2.	구체적으로 어떤 조치를 취해야 하는지 결정하세요. (예: strengthen, update_neighbor)
                2.1 strengthen를 선택한 경우, 어떤 메모리와의 연결을 강화해야 하는지 해당 메모리의 content를 제시하세요.
                2.2 update_neighbor를 선택한 경우, 새로운 메모리에 대한 현재 시점의 이해를 바탕으로 각 이웃 메모리의 문맥(context)을 갱신할 수 있습니다. 만약 문맥을 갱신할 필요가 없다면, 기존의 문맥을 그대로 사용하세요. 새로운 문맥은 입력받은 이웃 메모리 순서에 맞게 차례대로 각각 생성하세요.

        참고:
            new_context_neighborhood의 길이도 입력받은 이웃 메모리의 수와 동일해야 합니다.

        Args:
            should_evolve (bool):
            actions (list[Literal[&quot;strengthen&quot;, &quot;update_neighbor&quot;]]):
            suggested_connections (list[str]):
            new_context_neighborhood (list[str]):
        """
        return should_evolve, actions, suggested_connections, new_context_neighborhood

    def evolution_system(self, problem_card, neighbors_text, neighbor_number):
        prompt = self.evolution_prompt.format(
            context=problem_card["properties"]["context"],
            content=problem_card["properties"]["question"],
            keywords=problem_card["properties"]["keywords"],
            nearest_neighbors_memories=neighbors_text,
            neighbor_number=neighbor_number,
        )

        tool_chain = self.llm.bind_tools(
            [self.evolution_memory]
        ) | JsonOutputKeyToolsParser(first_tool_only=True, key_name="evolution_memory")
        result = tool_chain.invoke(prompt)
        return result
