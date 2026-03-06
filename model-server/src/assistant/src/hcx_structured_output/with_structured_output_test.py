# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import sys
from pathlib import Path
from typing import Literal

from langchain_core.tools import BaseTool, tool

# Add src directory to Python path
SRC_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC_DIR))

from adapters.clovax_hso import ChatClovaXHSO
from langchain_core.messages import HumanMessage
from schemas import build_model_from_spec
from utils import load_prompt_yaml

SYSTEM_RULES, FEWSHOTS = load_prompt_yaml("../prompt/prompt_generic.yaml")
MAX_RETRIES = 10

llm = ChatClovaXHSO(model="hcx-005")

# ex1
spec = {
    "setup": {
        "type": "str",
        "description": "The setup of the joke",
        "required": True,
    },
    "punchline": {"type": "str", "description": "The punchline"},
    "rating": {
        "type": "int",
        "description": "How funny the joke is, 1~10",
        "required": True,
    },
}

json_schema = build_model_from_spec(
    "joke", spec=spec, model_description="Joke to tell user."
)

structured = llm.with_structured_output(
    json_schema,
    include_raw=True,
    system_rules=SYSTEM_RULES,
    fewshots=FEWSHOTS,
    max_retries_for_fallback=MAX_RETRIES,
    debug=False,
)

# Test with string input
result = structured.invoke("Tell me a joke about cats")
print("String input result:", result)
print("=" * 100)

# Test with HumanMessage input
text_message = HumanMessage(content="Tell me a joke about cats")
result2 = structured.invoke([text_message])
print("HumanMessage input result:", result2)
print("=" * 100)

# ex2
spec = {
    "name": "str",
    "role": "str",
    "skills": "List[str]",
    "experience_years": "int",
}

json_schema = build_model_from_spec("PersonSummary", spec)

structured = llm.with_structured_output(
    json_schema,
    include_raw=True,
    system_rules=SYSTEM_RULES,
    fewshots=FEWSHOTS,
    max_retries_for_fallback=MAX_RETRIES,
    debug=False,
)

result = structured.invoke(
    "홍길동은 데이터 엔지니어이며 Python, Spark, Airflow에 능숙하다. 경력은 5년이다"
)
print(result)
print("=" * 100)

# ex3. Image structured output
# Define schema for image analysis
image_spec = {
    "question": {
        "type": "str",
        "description": "이미지의 문제",
        "required": True,
    },
    "explanation": {
        "type": "str",
        "description": "이미지의 문제 풀이과정",
        "required": True,
    },
    "answer": {
        "type": "str",
        "description": "이미지에 있는 문제에 대한 정답",
        "required": True,
    },
}

image_json_schema = build_model_from_spec(
    "ImageAnalysis",
    spec=image_spec,
    model_description="Analysis of educational problem image.",
)

SYSTEM_RULES, _ = load_prompt_yaml("../prompt/prompt_problem_info_image.yaml")
user_prompt = """사진에 보이는 문제의 question, explanation, answer만 포함하는 JSON을 생성합니다."""

# Create structured LLM
structured_llm = llm.with_structured_output(
    image_json_schema,
    include_raw=True,
    # system_rules=SYSTEM_RULES,
    # fewshots=FEWSHOTS,
    max_retries_for_fallback=MAX_RETRIES,
    debug=False,
)

# process a single image
image_url = "https://dimg.donga.com/wps/NEWS/IMAGE/2014/11/17/67941705.3.jpg"
msg = HumanMessage(
    content=[
        {"type": "text", "text": SYSTEM_RULES + "\n" + user_prompt},
        {"type": "image_url", "image_url": {"url": image_url}},
    ]
)

result = structured_llm.invoke([msg])
print("Image input result:", result)
print("=" * 100)


# ex4. tool_calling
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


@tool(description="문제를 풀 수 있는 도구")
def calculator(problem: str, answer: str) -> str:
    """
    간단한 산술/수학식을 계산합니다.

    Args:
        problem (str): 문제 정보

    Returns:
        answer (str): 문제 정답
    """
    return f"문제 정답은 {answer} 입니다."


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


tools: list[BaseTool] = [get_weather, calculator, reading_passage]
tool_bind_llm = llm.bind_tools(tools, max_retries=3)  # , parallel_tool_calls = True
msg = HumanMessage(
    content="서울 날씨좀 알려주세요 그리고 2+3이 뭔지도 알려주세요"
)  # multi tool choice
response = tool_bind_llm.invoke([msg])
# print(response.tool_calls)
print("Tool-calling results: ", response)
print("=" * 100)

msg = HumanMessage(
    content=[
        {"type": "text", "text": "이거 어떻게 풀어"},
        {"type": "image_url", "image_url": {"url": image_url}},
    ]
)
response = tool_bind_llm.invoke([msg])
print("\nImage Tool-calling results: ", response)
