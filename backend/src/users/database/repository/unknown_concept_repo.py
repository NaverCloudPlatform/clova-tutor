# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from collections.abc import Iterable
from dataclasses import dataclass

from base_repository import BaseRepoFilter, BaseRepository

from users.database.models import UserUnknownConceptModel
from users.domain.user_unknown_concept import UserUnknownConcept


@dataclass(slots=True)
class UserUnknownConceptFilter(BaseRepoFilter):
    id: int | Iterable[int] |  None = None

    # 유저 id
    user_id: uuid.UUID |  Iterable[uuid.UUID] | None = None

    # 과목 별 필터링
    subject: str | Iterable[str] |None = None

    # key_concept 별 필터링
    key_concept: str | Iterable[str]  | None = None


class UserUnknownConceptRepository(BaseRepository[UserUnknownConceptModel, UserUnknownConcept]):
    filter_class = UserUnknownConceptFilter


