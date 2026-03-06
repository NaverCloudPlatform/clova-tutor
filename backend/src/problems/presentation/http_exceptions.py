# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# FastAPI 애플리케이션에 예외 처리 핸들러를 등록하는 함수
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from common.presentation.response import http_error
from problems.service.exceptions import ProblemNotFoundException
from problems.usecase.exceptions import (
    ProblemAnswerTypeNotMatchException,
    ProblemGradeNotMatchException,
    ProblemLevelNotMatchException,
    ProblemSubjectNotMatchException,
)


def add_problems_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProblemNotFoundException)
    async def problem_not_found_handler(
        request: Request, exc: ProblemNotFoundException
    ) -> JSONResponse:
        return http_error(404,exc)

    @app.exception_handler(ProblemSubjectNotMatchException)
    async def problem_subject_not_match_handler(
        request: Request, exc: ProblemSubjectNotMatchException
    ) -> JSONResponse:
        return http_error(422, exc)

    @app.exception_handler(ProblemGradeNotMatchException)
    async def problem_grade_not_match_handler(
        request: Request, exc: ProblemGradeNotMatchException
    ) -> JSONResponse:
        return http_error(422, exc)

    @app.exception_handler(ProblemLevelNotMatchException)
    async def problem_level_not_match_handler(
        request: Request, exc: ProblemLevelNotMatchException
    ) -> JSONResponse:
        return http_error(422, exc)

    @app.exception_handler(ProblemAnswerTypeNotMatchException)
    async def problem_answer_type_not_match_handler(
        request: Request, exc: ProblemAnswerTypeNotMatchException
    ) -> JSONResponse:
        """ProblemAnswerTypeNotMatchException 발생 시 422 응답을 반환합니다."""
        return http_error(422, exc)
