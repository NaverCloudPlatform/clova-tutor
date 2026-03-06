# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from base_repository import BaseRepoFilter, BaseRepository
from pydantic import BaseModel
from sqlalchemy import Insert, func, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import literal

from problems.database.models import ProblemModel
from problems.database.problem_mapper import ProblemMapper
from problems.domain.problem import GradeEnum, Problem, SubjectEnum


@dataclass(slots=True)
class ProblemFilter(BaseRepoFilter):
    id: str | Iterable[str] | None = None

    subject: SubjectEnum | Iterable[SubjectEnum] | None = None

    grade: GradeEnum | Iterable[SubjectEnum] | None = None
    semester: int | Iterable[int] | None = None


class ProblemRepository(BaseRepository[ProblemModel, Problem]):
    filter_class=ProblemFilter
    mapper = ProblemMapper


    def _build_update_map(self, stmt: Insert, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not rows:
            return {}

        # rows 간 공통 컬럼만 UPDATE 대상으로 삼음
        common_keys = set(rows[0].keys())
        for r in rows[1:]:
            common_keys &= set(r.keys())

        common_keys.discard("id")
        common_keys.discard("created_at")
        common_keys.discard("updated_at")

        return {k: getattr(stmt.inserted, k) for k in common_keys}  # type: ignore[attr-defined]

    async def upsert_many(
        self,
        items: Sequence[BaseModel | Mapping[str, Any]],
        *,
        session: AsyncSession | None= None,
    ) -> None:
        objs = [self._schema_to_orm(data) for data in items]
        s = self._resolve_session(session)

        objs_dict = [
            {
                c.name: getattr(obj, c.name)
                for c in obj.__table__.columns
                if c.name not in ("created_at", "updated_at")
            }
            for obj in objs
        ]
        stmt = mysql_insert(self.model).values(objs_dict)
        update_map = self._build_update_map(stmt, objs_dict)
        stmt = stmt.on_duplicate_key_update(update_map)

        await s.execute(stmt)


    async def find_random_problem_not_duplicated(
        self,
        flt: ProblemFilter,
        exclude_ids: Iterable[str]
    ) -> Problem | None:
        if exclude_ids:
            filter_exclude = ProblemModel.id.not_in(exclude_ids)
        else:
            filter_exclude = literal(True) # type: ignore

        random_func = func.random()

        crit = flt.where_criteria(self.model)

        s = self._resolve_session(None)
        stmt = (
            select(ProblemModel)
            .where(
                *crit,
                filter_exclude
            )
            .order_by(random_func)
            .limit(1)
        )

        row = await s.execute(stmt)
        res = row.scalar_one_or_none()
        if not res:
            return None
        return self._convert(res, convert_schema=None)
