# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC_DIR))

from typing import Literal, Optional

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field, conlist, constr

from src.adapters.clovax_hso import ChatClovaXHSO

ShortStr = constr(min_length=3, max_length=60)
SummaryStr = constr(min_length=30, max_length=300)


class PassageParse(BaseModel):
    topic: ShortStr = Field(..., description="짧은 명사구")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        ..., description="난이도 수준"
    )
    core_summary: SummaryStr = Field(..., description="문단의 핵심을 1~2문장으로 요약")
    key_points: conlist(ShortStr, min_length=3, max_length=6) = Field(
        ..., description="핵심 포인트 3~6개 (각 60자 이내)"
    )
    attention_mentioned: bool = Field(
        ..., description="문단에 Attention이 언급되었는지"
    )
    category: ShortStr = Field(..., description="한 단어로 문단의 주제를 분류")


SYSTEM_RULES = (
    "Read the user's passage and return EXACTLY ONE JSON object with keys: "
    "topic, difficulty, core_summary, key_points, attention_mentioned, category.\n"
    "- topic: short noun phrase in English (<=60 chars).\n"
    "- difficulty: one of ['beginner','intermediate','advanced'].\n"
    "- core_summary: 1-2 sentences (30-300 chars), no citations.\n"
    "- key_points: 3-6 atomic bullet-style items (<=60 chars each), no numbering.\n"
    "- attention_mentioned: boolean.\n"
    "- category: one-word topic classification.\n"
    "No code fences. No extra text. JSON ONLY."
)


class RecommendProblemArgs(BaseModel):
    """학생이 문제를 **추천**을 요청하거나 학생의 문제 풀이가 **완료**되었을 때 이 도구를 무조건 제발 호출해주세요."""

    recommend: bool = Field(
        description=(
            "학생이 문제를 추천할 의도가 있는지 여부\n"
            "- True  : '문제 추천해줘', '비슷한 문제', '연습문제 주라' 등 **추천 의도**일 때\n"
            "- False : 명시적 완료/이해/정답 확인 또는 '다음 문제' 신호가 있을 때만\n"
            "          (예: '이해했어', '알겠어', '정답이 8이지?', '다 풀었어', '다음 문제')"
        ),
    )
    more_difficult: bool = Field(
        description=(
            "난이도 상향 여부. None이라고 판단하면 무조건 False로 처리해주세요.\n"
            "- True  : '더 어려운/심화' 등 명시적 상향 요청이 있을 때\n"
            "- False : 특정 난이도 언급이 없거나, 단순히 비슷한 문제를 요청했을 때"
        ),
    )


@tool(
    args_schema=RecommendProblemArgs,
)
def recommend_problem_tool(
    recommend: bool = None,
    more_difficult: bool = None,
):
    print("--------------------------------" * 10)
    print("recommend_problem_tool results")
    print("recommend", recommend)
    print("more_difficult", more_difficult)
    return f"recommend: {recommend}, more_difficult: {more_difficult}"


@tool(
    description="""
    학생이 영어 단어를 질의할 때 해당 도구를 무조건 호출하세요.
    """,
    args_schema=RecommendProblemArgs,
)
def voca_tool(
    voca: Optional[dict[str, list[int]]] = None,
):
    print("voca", voca)
    return f"voca: {voca}"


if __name__ == "__main__":

    """
    This example uses text from the paper:

    Attention Is All You Need
    Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin
    NeurIPS 2017

    ArXiv: https://arxiv.org/abs/1706.03762

    Source: Vaswani et al., "Attention Is All You Need", NeurIPS 2017 (arXiv:1706.03762)
    """

    passage = "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data."

    hcx = ChatClovaXHSO(model="HCX-005")

    # 2) with_structured_output → _FallbackRunnable 경로로 호출
    # structured = hcx.with_structured_output(
    #     schema=PassageParse,
    #     system_rules=SYSTEM_RULES,
    #     temperature_for_fallback=0.2,
    #     max_retries_for_fallback=5,  #
    #     retry_mode_for_fallback="manual",  #
    #     include_raw=True,
    #     language="ko",
    #     backend_for_fallback="langchain",
    #     debug=True,
    # )

    # out = structured.invoke(passage)  # _FallbackRunnable.invoke → run_structured_task
    # parsed = out["parsed"]
    # raw = out["raw"]
    # meta = getattr(raw, "response_metadata", {}) or {}

    # print("\n[PARSED]", parsed)
    # print("[ATTEMPTS]", meta.get("attempts"))
    # print("[USAGE total]", meta.get("token_usage_total"))

    tools = [recommend_problem_tool]
    hcx_graph = create_react_agent(hcx, tools=tools)
    hcx_agent_with_recursion_limit = hcx_graph.with_config(recursion_limit=10)

    inputs = {
        "messages": [
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "문제 추천해줘",
                    },
                ]
            )
        ]
    }

    response = hcx_agent_with_recursion_limit.invoke(inputs)
    print(response)
