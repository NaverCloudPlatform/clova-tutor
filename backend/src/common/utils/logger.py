# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import logging

from enum import StrEnum
from typing import Any

from config.config import env_config


class ServiceLogType(StrEnum):
    BUSINESS = "BUSINESS"  # 일반적인 비지스니 로직을 의미합니다.
    SYSTEM = "SYSTEM"  # 시스템의 내부 동작, 구성, 시작/종료, 리소스 사용 등 애플리케이션 자체가 아닌 기반 시스템이나 프레임워크 수준의 로그
    SECURITY = "SECURITY"  # 잠재적인 보안 위협이나 공격 시도, 비정상적인 접근 패턴 등을 기록합니다.
    AUDIT = "AUDIT"  # 보안 및 규제 준수를 위한 중요한 사용자 행위나 시스템 변경 사항을 기록합니다.


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1


def setup_logger(name: str, level: int) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.addFilter(HealthCheckFilter())

    logger.propagate = False

    # console handler 없으면 추가
    is_console_handler_present = any(
        isinstance(h, logging.StreamHandler) for h in logger.handlers
    )

    if not is_console_handler_present:
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(levelname)s - %(name)s - %(asctime)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


app_logger = setup_logger("service", logging.DEBUG)

# FASTAPI 기본 로그 레벨 설정
setup_logger("uvicorn.error", logging.ERROR)
setup_logger("uvicorn.access", logging.INFO)


def register_internal_service_log(
    msg: str,
    log_type: ServiceLogType = ServiceLogType.BUSINESS,
    level: int = logging.INFO,
    *args: object,
    **kwargs: Any,
) -> None:
    """
    내부 서비스 로그를 지정된 레벨과 타입으로 등록합니다.
    Args:
        msg (str): 로그 메시지.
        log_type (ServiceLogType): 로그의 유형 (예: ServiceLogType.BUSINESS, ServiceLogType.SYSTEM 등).
                                   기본값은 ServiceLogType.BUSINESS.
        level (int): 로그 레벨 (예: logging.INFO, logging.ERROR 등). 기본값은 logging.INFO.
        *args: 로그 메시지의 포매팅에 사용될 추가 인자들.
        **kwargs: 로깅 시스템에 전달될 추가 키워드 인자들 (예: exc_info, stack_info, extra).
    """
    extra_data = {"serviceLogType": log_type.value}

    if "extra" in kwargs:
        kwargs["extra"].update(extra_data)
    else:
        kwargs["extra"] = extra_data

    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1

    # 선택된 레벨에 따라 app_logger의 해당 메서드를 호출
    if level == logging.DEBUG:
        app_logger.debug(msg, *args, **kwargs)
    elif level == logging.INFO:
        app_logger.info(msg, *args, **kwargs)
    elif level == logging.WARNING:
        app_logger.warning(msg, *args, **kwargs)
    elif level == logging.ERROR:
        app_logger.error(msg, *args, **kwargs)
    elif level == logging.CRITICAL:
        app_logger.critical(msg, *args, **kwargs)
    else:
        app_logger.info(msg, *args, **kwargs)
