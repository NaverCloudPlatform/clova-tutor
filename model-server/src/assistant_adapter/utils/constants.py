# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

CHAT_TITLE_CREATE_PROMPT = "Summarize the student's request into a concise title focusing on the core topic or input type.\n\nInstructions:\n\n- If it's a concept question -> Title as 'Concept: [Topic]' (e.g., 개념: 피타고라스)\n\n- If it's a problem-solving request -> Title as 'Problem [Number/Type]' (e.g., 2024 수능 30번 풀이)\n\n- If it's translation/writing -> Title as '[Type] Practice' (e.g., 영어 에세이 첨삭)\n\n- **[IMPORTANT] Non-Educational / Vague / Random Inputs:**\n\n- Even if the input is NOT related to education or is gibberish, **summarize the content itself or the type of input**.\n\n- Do NOT output error messages like 'I cannot understand.'\n\n- Examples:\n\n- 'Hello', 'Hi' -> '가벼운 인사'\n\n- 'ㄴㄷㄱㄴㄷㄴㅇㄹ', 'asdf' -> '무작위 문자 입력'\n\n- 'I'm bored', 'Simsimhae' -> '일상 대화'\n\n- '???', '...' -> '의미 불명확한 입력'\n\n- Keep it extremely short and noun-focused (max 5 words).\n\n- **STRICTLY return ONLY the title text.**\n\nExample:\n\nUser Input: '이거 문법 맞는지 봐주라'\n\nOutput: 영어 문법 첨삭\n\n\n\nUser Input: '삼각함수 덧셈정리 증명해줘'\n\nOutput: 개념: 삼각함수 덧셈정리 \n\n\n\n Real Input : "


def make_chat_title_prompt(input: str) -> str:
    return CHAT_TITLE_CREATE_PROMPT + input
