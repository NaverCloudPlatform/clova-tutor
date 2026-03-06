# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import logging


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1


logger = logging.getLogger("uvicorn")

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.addFilter(HealthCheckFilter())
