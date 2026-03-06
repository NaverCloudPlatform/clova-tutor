# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# examples/run_generic.py
from src.schemas import build_model_from_spec
from src.utils import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    load_prompt_yaml,
    run_structured_task,
)

SYSTEM_RULES, FEWSHOTS = load_prompt_yaml("../prompt/prompt_generic.yaml")

spec = {
    "service": "str",
    "endpoints": "List[str]",
    "auth": {"enum": ["none", "api_key", "oauth2", "other"]},
}
ResponseModel = build_model_from_spec("ApiSummary", spec)

user_text = (
    "문서에서 서비스명, 엔드포인트 목록(최대 5개), 인증 방식을 추출.\n"
    'schema: {"service":str,"endpoints":List[str],"auth":enum["none","api_key","oauth2","other"]}\n'
    "문서:\n"
    "Weather API는 /current, /forecast, /historical 엔드포인트를 제공하며, API 키가 필요하다."
)

res = run_structured_task(
    system_rules=SYSTEM_RULES,
    fewshots=FEWSHOTS,
    user_content={"role": "user", "content": [{"type": "text", "text": user_text}]},
    response_model=ResponseModel,
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_retries=DEFAULT_MAX_RETRIES,
)
print(res.model_dump())
