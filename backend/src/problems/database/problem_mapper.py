# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from typing import Any

from base_repository import BaseMapper
from pydantic import TypeAdapter

from problems.database.models import ProblemModel
from problems.domain.problem import Answer, Problem, ProblemChoice


class ProblemMapper(BaseMapper):
    def __init__(self) -> None:
        self._tag_adapter = TypeAdapter(list[str])
        self._answer_adapter = TypeAdapter(list[Answer])
        self._choice_adapter = TypeAdapter(list[ProblemChoice])

    def to_orm(self, domain_object: Problem) -> ProblemModel:
        tags_str = None
        if domain_object.tags is not None:
            tags_str = self._tag_adapter.dump_json(domain_object.tags).decode()

        choice_str = None
        if domain_object.choices is not None:
            choice_str = self._choice_adapter.dump_json(domain_object.choices).decode()

        correct_answers_str = self._answer_adapter.dump_json(domain_object.correct_answers).decode()

        domain_dict = domain_object.model_dump(
            exclude={Problem.FIELD_TAGS, Problem.FIELD_CHOICES, Problem.FIELD_CORRECT_ANSWERS}
        )
        return ProblemModel(
            **domain_dict,
            tags=tags_str,
            choices=choice_str,
            correct_answers=correct_answers_str
        )


    def to_schema(self, orm_object: ProblemModel) -> Problem:
        tags: list[str] | None = None
        if orm_object.tags is not None:
            tags = self._tag_adapter.validate_json(orm_object.tags)

        choices: list[ProblemChoice] | None = None
        if orm_object.choices is not None:
            choices = self._choice_adapter.validate_json(orm_object.choices)

        correct_answers: list[Answer] = self._answer_adapter.validate_json(orm_object.correct_answers)

        orm_dict: dict[str, Any] = orm_object.__dict__.copy()
        orm_dict.update({
            Problem.FIELD_TAGS: tags,
            Problem.FIELD_CHOICES: choices,
            Problem.FIELD_CORRECT_ANSWERS: correct_answers,
        })

        return Problem.model_validate(orm_dict)
