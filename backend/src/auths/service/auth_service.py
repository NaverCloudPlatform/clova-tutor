# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT


from uuid import UUID

from fastapi import Request

from auths.service.exceptions import HeaderNotExistException, HeaderTypeNotMatchException


class AuthService:
    async def get_user_id_from_header(
        self,
        request: Request
    ) -> UUID:
        user_id_str = request.headers.get("X-User-Id", None)
        if user_id_str is None:
            raise HeaderNotExistException()

        try:
            user_id = UUID(user_id_str)
            return user_id
        except ValueError:
            raise HeaderTypeNotMatchException(user_id_str)
