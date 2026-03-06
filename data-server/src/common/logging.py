# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from logging import getLogger, Formatter, Logger

from rich.logging import RichHandler

import logging

class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.addFilter(HealthCheckFilter())


def set_logger(logger_name: str, log_level: str) -> Logger:
    logger = getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = False

    if len(logger.handlers) > 0:
        # 핸들러 중복 추가 방지 (백엔드 측 필요)
        return logger

    handler = RichHandler(rich_tracebacks=True)
    handler.setLevel(log_level)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
