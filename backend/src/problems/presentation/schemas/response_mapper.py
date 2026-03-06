# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from pydantic import TypeAdapter

from problems.domain.problem import Problem
from problems.presentation.schemas.response_dto import ProblemDetail, ProblemResponse


class ProblemResponseMapper:
    @staticmethod
    def to_response(
        problem: Problem
    ) -> ProblemResponse:
        _adapter: TypeAdapter[ProblemDetail] = TypeAdapter(ProblemDetail)

        problem_dict = {
            "id" : problem.id,
            "type" : problem.type,
            "content": problem
        }

        contnet_schema = _adapter.validate_python(problem_dict)

        return ProblemResponse(
            contnet_schema
        )
