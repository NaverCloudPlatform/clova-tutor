# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import Iterable
from typing import cast

from problems.database.repository import ProblemFilter, ProblemRepository
from problems.domain.problem import (
    GradeEnum,
    Problem,
    ProblemAnswerType,
    SubjectEnum,
    is_choice_answer,
    is_short_answer,
)
from problems.service.exceptions import ProblemNotFoundException


class ProblemService:
    def __init__(self, problem_repo: ProblemRepository) ->  None:
        self.problem_repo = problem_repo

    async def get_problems_by_subject_and_grade(
        self, subject: SubjectEnum, grade: GradeEnum
    ) -> list[Problem]:
        """
        주어진 subject, grade에 맞는 문제 목록을 검색하여 Problem 리스트로 반환
        """
        problems: list[Problem] = await self.problem_repo.get_list(
            flt=ProblemFilter(subject=subject, grade=grade)
        )
        return problems


    async def get_problem_by_id(
        self, id: str
    ) -> Problem:
        problem : Problem | None = await self.problem_repo.get(flt=ProblemFilter(id=id))
        if problem is None:
            raise ProblemNotFoundException(id)
        return problem

    async def get_problems_by_ids(
        self,
        ids: Iterable[str]
    ) -> list[Problem]:
        problems: list[Problem] = await self.problem_repo.get_list(flt=ProblemFilter(id=ids))
        return problems


    async def find_random_problem(
        self,
        exclude_ids: list[str],
        subject: SubjectEnum | None = None,
        grade: GradeEnum | None = None,
        semester: int | None = None,
    ) -> Problem | None:
        problem: Problem | None = await self.problem_repo.find_random_problem_not_duplicated(
            flt=ProblemFilter(
                subject=subject,
                grade=grade,
                semester=semester
            ),
            exclude_ids=exclude_ids
        )
        return problem


    async def create_problems(
        self,
        problems: list[Problem]
    ) -> list[Problem]:
        await self.problem_repo.upsert_many(
            problems
        )

        ids_to_find = [p.id for p in problems]

        ps = await self.get_problems_by_ids(
            ids=ids_to_find
        )

        return ps


    async def submit_problem_answer(
        self,
        problem_id: str,
        submitted_answer: int | list[int] | str | list[str]
    ) -> bool:
        problem = await self.get_problem_by_id(problem_id)

        is_correct = False
        if is_choice_answer(problem):
            answer_for_choice = cast('int | list[int]', submitted_answer)
            is_correct = self._check_choice_answer(problem, answer_for_choice)

        elif is_short_answer(problem):
            answer_for_short = cast('str | list[str]', submitted_answer)
            is_correct = self._check_short_answer(problem, answer_for_short)

        return is_correct


    def _check_choice_answer(
        self,
        problem: Problem,
        submitted_answer: int | list[int]
    ) -> bool:
        correct_answers = [int(ans.answer) for ans in problem.correct_answers]
        if problem.type == ProblemAnswerType.SINGLE_CHOICE_ANSWER:
            if isinstance(submitted_answer, int):
                return submitted_answer == correct_answers[0]

            elif isinstance(submitted_answer, list) and len(submitted_answer) == 1:
                 return submitted_answer[0] == correct_answers[0]

        if problem.type == ProblemAnswerType.MULTIPLE_CHOICE_ANSWER:
            if isinstance(submitted_answer, list):
                return set(submitted_answer) == set(correct_answers)

        return False

    def _check_short_answer(
        self,
        problem: Problem,
        submitted_answer: str | list[str]
    ) -> bool:
        correct_answers = problem.correct_answers

        if problem.type == ProblemAnswerType.SINGLE_SHORT_ANSWER and isinstance(submitted_answer, str):
            for ans in correct_answers:
                accepted = ans.accepted_answers if ans.accepted_answers else []
                valid = {ans.answer, *accepted}
                if submitted_answer in valid:
                    return True
            return False

        if problem.type == ProblemAnswerType.MULTIPLE_SHORT_ANSWER:
            remaining_submitted = set(submitted_answer)

            for required_answer_obj in correct_answers:

                allowed_variants = {required_answer_obj.answer}
                if required_answer_obj.accepted_answers:
                    allowed_variants.update(required_answer_obj.accepted_answers)

                found_match = False

                for submitted_sa in remaining_submitted:
                    if submitted_sa in allowed_variants:
                        remaining_submitted.remove(submitted_sa)
                        found_match = True
                        break

                if not found_match:
                    return False
            if remaining_submitted:
                return False

            return True

        return False

