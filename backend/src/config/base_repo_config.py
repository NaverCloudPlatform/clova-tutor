# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from base_repository.session_provider import SessionProvider
from sqlalchemy.ext.asyncio import AsyncSession

from common.infra.mysql.mysql import Mysql


class MysqlSessionProvider(SessionProvider):
    def get_session(self) -> AsyncSession:
        return Mysql.current_session()
