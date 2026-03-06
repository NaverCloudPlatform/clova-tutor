# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import uuid

from typing import Any, cast
from uuid import UUID

from users.database.models import UserModel
from users.database.repository.user_repo import UserFilter, UserRepository
from users.domain.user import User, UserWithDate
from users.service.exceptions import UserNotFoundException


class UserService:
    def __init__(
        self,
        user_repo: UserRepository
    ):
        """UserService 초기화

        Args:
            user_repo (UserRepository): 사용자 저장소 객체
        """
        self.user_repo = user_repo

    async def get_user_list(self) -> list[UserWithDate]:
        """모든 사용자 목록을 조회합니다.

        Returns:
            List[User]: 사용자 목록 DTO
        """
        users = await self.user_repo.get_list(
            order_by=[UserModel.updated_at.desc()],
            convert_schema=False
        )

        return [
            UserWithDate.model_validate(user)
            for user in users
        ]

    async def get_user_by_id(self, user_id: UUID) -> UserWithDate:
        """특정 사용자를 조회합니다.

        Args:
            user_id (UUID): 사용자 ID

        Returns:
            User: 조회된 사용자 DTO
        """
        user = await self.user_repo.get(
            UserFilter(id=user_id),
            convert_schema=False
        )
        if user is None:
            raise UserNotFoundException(user_id)

        return UserWithDate.model_validate(user)

    async def create_user(
        self,
        name: str,
        grade: int,
        memo: str | None
    ) -> User:
        """새로운 사용자를 생성합니다.

        Args:
            name (str)
            grade (int)
            memo (str | None)

        Returns:
            User: 생성된 사용자 DTO
        """
        obj_in = User(
            id=uuid.uuid4(),
            name=name,
            grade=grade,
            memo=memo
        )
        new_user: User = await self.user_repo.create(obj_in)
        return new_user

    async def update_user(
        self,
        user_id: UUID,
        update_dict: dict[str, Any]
    ) -> UserWithDate:
        user_model =  await self.user_repo.get(flt=UserFilter(id=user_id), convert_schema=False)
        if not user_model:
            raise UserNotFoundException(user_id)

        updated = cast(UserWithDate, await self.user_repo.update_from_model(
            user_model,
            update=update_dict,
        ))
        return updated

    async def delete_user(self, user_id: UUID) -> None:
        """특정 사용자를 삭제합니다.

        Args:
            user_id (UUID | str)
        """
        await self.user_repo.delete(
            UserFilter(id=user_id)
        )
