# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from common.utils.utils import attach_timezone
from users.presentation.schemas.request_dto import UserCreateRequestBody, UserUpdateRequestBody
from users.presentation.schemas.response_dto import (
    UserCreateResponse,
    UserResponse,
    UserUpdateResponse,
)
from users.service.exceptions import UserNotFoundException
from users.service.user_service import UserService


class UserUseCase:
    def __init__(
        self,
        user_service: UserService
    ) -> None:
        self.user_service = user_service

    async def _validate_user_id(self, user_id: UUID) -> None:
        user = await self.user_service.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)


    async def get_users(
        self
    ) -> list[UserResponse]:
        """
        모든 사용자 목록을 조회합니다.
        """
        users = await self.user_service.get_user_list()
        return [
            UserResponse(
                id=user.id,
                name=user.name,
                grade=user.grade,
                memo=user.memo,
                created_at=attach_timezone(user.created_at),
                updated_at=attach_timezone(user.updated_at)
            ) for user in users
        ]


    async def get_user_by_id(
        self,
        user_id: UUID
    ) -> UserResponse:
        user = await self.user_service.get_user_by_id(user_id)
        return UserResponse(
            id=user.id,
            name=user.name,
            grade=user.grade,
            memo=user.memo,
            created_at=attach_timezone(user.created_at),
            updated_at=attach_timezone(user.updated_at)
        )


    async def create_user(
        self,
        body: UserCreateRequestBody
    ) -> UserCreateResponse:
        user = await self.user_service.create_user(
            name=body.name,
            grade=body.grade,
            memo=body.memo
        )
        return UserCreateResponse(
            id=user.id,
            name=user.name,
            grade=user.grade,
            memo=user.memo,
        )


    async def patch_user(
        self,
        user_id: UUID,
        body: UserUpdateRequestBody
    ) -> UserUpdateResponse:
        await self._validate_user_id(user_id)

        user = await self.user_service.update_user(
            user_id,
            update_dict=body.model_dump(exclude_unset=True)
        )
        return UserUpdateResponse(
            id=user.id,
            name=user.name,
            grade=user.grade,
            memo=user.memo
        )

    async def delete_user(
        self,
        user_id: UUID
    ) -> None:
        await self._validate_user_id(user_id)
        await self.user_service.delete_user(user_id)
