# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


from problems.domain.problem import GradeEnum, Problem, ProblemAnswerType, ProblemLevel, SubjectEnum
from problems.presentation.schemas.request_dto import ProblemCreateRequestBody
from problems.presentation.schemas.response_dto import (
    ProblemCreateResponse,
    ProblemResponse,
)
from problems.presentation.schemas.response_mapper import ProblemResponseMapper
from problems.service.problem_service import ProblemService
from problems.usecase.exceptions import (
    ProblemAnswerTypeNotMatchException,
    ProblemGradeNotMatchException,
    ProblemLevelNotMatchException,
    ProblemSubjectNotMatchException,
)


class ProblemUseCase:
    def __init__(
        self,
        problem_service: ProblemService
    ):
        self.problem_service = problem_service


    async def get_problem(
        self, problem_id: str
    ) -> ProblemResponse:
        problem = await self.problem_service.get_problem_by_id(problem_id)

        return ProblemResponseMapper.to_response(problem)


    async def create_bulk_problems(
        self,
        body: ProblemCreateRequestBody
    ) -> ProblemCreateResponse:
        problems: list[Problem] = []

        if len(body.problems) == 0:
            return ProblemCreateResponse(ids=[])

        for prob in body.problems:

            # 1. subject
            if prob.subject == "영어":
                prob.subject = "english"
            elif prob.subject == "수학":
                prob.subject = "math"
            subject: SubjectEnum | None = None
            try:
                subject = SubjectEnum(prob.subject)
            except Exception:
                raise ProblemSubjectNotMatchException(prob.subject)

            # 2. grade
            grade: GradeEnum | None = None
            try:
                grade = GradeEnum(prob.grade)
            except Exception:
                raise ProblemGradeNotMatchException(prob.grade)

            # 3. level
            level: ProblemLevel | None = None
            try:
                level = ProblemLevel(prob.level)
            except Exception:
                raise ProblemLevelNotMatchException(prob.level)

            # 4. AnswerType
            answer_type: ProblemAnswerType | None = None
            try:
                answer_type = ProblemAnswerType(prob.type)
            except Exception:
                raise ProblemAnswerTypeNotMatchException(prob.type)

            created = Problem(
                **prob.model_dump(exclude={Problem.FIELD_SUBJECT, Problem.FIELD_GRADE, Problem.FIELD_LEVEL, Problem.FIELD_TYPE}),
                subject=subject,
                grade=grade,
                level=level,
                type=answer_type
            )

            problems.append(created)

        res = await self.problem_service.create_problems(problems)

        return ProblemCreateResponse(
            ids= [r.id for r in res]
        )
