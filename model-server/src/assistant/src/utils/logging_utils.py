# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from logging import FileHandler, Formatter, Logger, getLogger

from rich.logging import RichHandler


def set_logger(logger_name: str, log_level: str, output_filename: str = "") -> Logger:
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

    if output_filename:
        # Add file handler
        file_handler = FileHandler(
            f"assistant/output/{output_filename}.log", encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def serialize(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)
