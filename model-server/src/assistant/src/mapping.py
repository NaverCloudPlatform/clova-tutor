# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from enum import Enum, IntEnum


class QueryEvaluationMap(IntEnum):
    QUESTION = 1  # 질문
    CORRECT = 2  # 정답
    INCORRECT = 3  # 오답


class ResponseStyleMapEng(IntEnum):
    TRANSLATION = 1  # 직독 직해
    TABLE_FETCH = 2  # 테이블 (단어/문법) DB FETCH
    ANSWER_INCLUDED = 3  # 문제 해설
    RECOMMEND_PROBLEM = 4  # 문제 추천
    DEFAULT_CHAT = 5  # 기타 질의

    def __str__(self):
        return self.name


class ResponseStyleMapMath(IntEnum):
    MATH_CONCEPT = 1  # 수학 개념 설명
    STEPWISE_SOLUTION = 2  # 단계별 풀이
    RECOMMEND_PROBLEM = 3  # 문제 추천
    DEFAULT_CHAT = 4  # 기타 질의

    def __str__(self):
        return self.name


class LearningPhaseMap(IntEnum):
    DEFINITION = 1  # 개념 설명
    ANALYSIS = 2  # 문장 해석
    ANSWER_INCLUDED = 3  # 풀이 제공
    RECOMMEND_PROBLEM = 4  # 비슷한 문제 제공
    COMPLETION_FEEDBACK = 5  # 문제 완료에 대한 피드백


class ErrorType(str, Enum):
    RATELIMIT = "ratelimit"
    PARSE = "parse"
    UNKNOWN = "unknown"
