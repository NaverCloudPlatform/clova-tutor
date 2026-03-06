# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from fastapi import Depends, Request

from auths.service.auth_service import AuthService
from users.dependencies import get_user_service
from users.domain.user import User
from users.service.user_service import UserService


async def get_auth_service() -> AuthService:
    return AuthService()


async def get_current_user_id(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> UUID:
    return await auth_service.get_user_id_from_header(request)


async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_user_by_id(user_id=user_id)

