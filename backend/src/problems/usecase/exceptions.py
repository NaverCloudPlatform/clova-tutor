# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from problems.service.exceptions import ProblemException


class ProblemSubjectNotMatchException(ProblemException):
    """문제의 Subject(과목)이 유효하지 않을 때 발생하는 예외"""
    default_msg = "유효하지 않은 과목(Subject) 값입니다."

    def __init__(self, invalid_subject: str):
        super().__init__(
            data={"subject": invalid_subject}
        )

# 문제 Grade(학년) 매칭 예외
class ProblemGradeNotMatchException(ProblemException):
    """문제의 Grade(학년)이 유효하지 않을 때 발생하는 예외"""
    default_msg = "유효하지 않은 학년(Grade) 값입니다"
    def __init__(self, invalid_grade: int | str):
        super().__init__(
            data={"grade" : invalid_grade}
        )

# 문제 Level(난이도) 매칭 예외
class ProblemLevelNotMatchException(ProblemException):
    """문제의 Level(난이도)이 유효하지 않을 때 발생하는 예외"""
    default_msg = "유효하지 않은 난이도(Level) 값입니다"
    def __init__(self, invalid_level: int | str):
        super().__init__(
            data={"level": invalid_level}
        )

# 문제 AnswerType(답변 유형) 매칭 예외
class ProblemAnswerTypeNotMatchException(ProblemException):
    """문제의 AnswerType(답변 유형)이 유효하지 않을 때 발생하는 예외"""
    default_msg = "유효하지 않은 답변 유형(AnswerType) 값입니다"
    def __init__(self, invalid_type: str):
        super().__init__(
            data={"answer_type" : invalid_type}
        )
