# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from collections.abc import Iterable
from dataclasses import dataclass

from base_repository import BaseRepoFilter, BaseRepository

from users.database.models import UserModel
from users.domain.user import User


@dataclass(slots=True)
class UserFilter(BaseRepoFilter):
    id: uuid.UUID | Iterable[uuid.UUID] | None = None


class UserRepository(BaseRepository[UserModel, User]):
    filter_class = UserFilter
