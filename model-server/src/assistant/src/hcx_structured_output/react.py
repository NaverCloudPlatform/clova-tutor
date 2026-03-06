# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from typing_extensions import Literal

from .src.adapters.clovax_hso import ChatClovaXHSO

hcx = ChatClovaXHSO(model="HCX-005")


def content_to_text(c):
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(
            b.get("text", "")
            for b in c
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return "" if c is None else str(c)


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


@tool(description="날씨 정보를 얻는 도구")
def get_weather(city: Literal["서울", "부산"]) -> str:
    """
    도시별 간단한 날씨 요약을 반환합니다.

    Args:
        city (Literal["서울","부산"]): 날씨를 조회할 도시 이름.

    Returns:
        str: 해당 도시의 간단한 날씨 설명.
    """
    return "서울은 흐릴 것 같아요" if city == "서울" else "부산은 항상 맑아요"


@tool(
    description="수학 문제를 풀 수 있는 도구. 사용자가 문제 풀이를 원하면 해당 도구를 선택하세요."
)
def calculator(problem: str, explanation: str, answer: str) -> str:
    """
    간단한 산술/수학식을 계산합니다.

    Args:
        problem (str): 문제 정보
        explanation (str): 문제 해설
        answer (str): 문제 정답

    Returns:
        answer_string (str): 문제 풀이와 정답
    """
    return f"문제 정답은 {answer} 이고, 풀이과정은 {explanation} 입니다."


@tool(description="이미지 속 영어 지문을 읽어 주요 문장을 반환하는 도구")
def reading_passage(passage: str) -> str:
    """
    문제를 읽어 문장을 OCR하는 도구 (더미 구현).
    Args:
        passage (str): 영어 지문.
    Returns:
        str: 영어 지문의 주요 문장 (더미 값).
    """
    return "영어 지문의 주요 문장"


tools = [get_weather, calculator, reading_passage]
image_url = "https://dimg.donga.com/wps/NEWS/IMAGE/2014/11/17/67941705.3.jpg"
inputs = {
    "messages": [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "x^2-4x+4=0 에서 이거 해 어떻게 구해",
                },
                # {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
    ]
}

print("=" * 50, "HCX-005", "=" * 50)
hcx_graph = create_react_agent(hcx, tools=tools)
hcx_agent_with_recursion_limit = hcx_graph.with_config(recursion_limit=10)
print_stream(hcx_agent_with_recursion_limit.stream(inputs, stream_mode="values"))

## message-streaming
print("=" * 50, "HCX-005", "=" * 50)
for mode, (msg, meta) in hcx_agent_with_recursion_limit.stream(
    inputs, stream_mode=["messages"]
):
    if isinstance(msg, AIMessageChunk):
        if msg.additional_kwargs.get("final_response", None):
            print(content_to_text(msg.content), end="", flush=True)
            finish = getattr(msg, "response_metadata", {}).get("finish_reason")
            if finish == "stop":
                print()
    elif isinstance(msg, AIMessage):
        pass
print("=" * 100)
