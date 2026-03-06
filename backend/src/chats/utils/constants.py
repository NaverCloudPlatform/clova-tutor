# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

SWAGGER_EXAMPLE_SSE = (
    "event: message_start\n"
    "data: {\n"
    '  "id": -1,\n'
    '  "chat_id": 1,\n'
    '  "created_at": "현재시간",\n'
    '  "type": "message",\n'
    '  "author": {\n'
    '    "role": "assistant",\n'
    '    "user_id": -1\n'
    "  },\n"
    '  "content": {\n'
    '    "m_type": "text",\n'
    '    "value": {\n'
    '      "text": ""\n'
    "    }\n"
    "  }\n"
    "}\n\n"
    "event: message_delta\n"
    'data: {"text": "string"}\n\n'
    "event: message_end\n"
)


RANDOM_PROBLEM_FOUND_TEXT = (
    "딱 맞는 문제는 아니지만, 이 문제도 꽤 괜찮아 보여! 한 번 풀어볼래?"
)


PROBLEM_ERROR_TEXT = (
    "이 단원에서 추천해줄 문제가 더 있으면 좋겠는데... "
    "아쉽게도 네가 전부 풀었어! 대단한 걸?"
)

ERROR_TEXT = (
    "일시적인 문제로 응답을 불러오지 못했어. 잠시 후 다시 시도해줄래?"
)
