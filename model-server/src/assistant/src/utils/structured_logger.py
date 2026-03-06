# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
from datetime import datetime
from enum import Enum
from logging import Logger
from typing import Any, Dict, Optional

from assistant.src.utils.logging_utils import serialize


class LogType(Enum):
    """Log type definition"""

    USER_QUERY = "user_query"
    LLM_CALL = "llm_call"
    NODE_EXECUTION = "node_execution"
    STATE_CHANGE = "state_change"
    ERROR = "error"
    USER_INFO = "user_builder"  # Changed from USER_BUILDER for clarity


class LogLevel(Enum):
    """Log level definition"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    # CRITICAL = "critical"  # Not used (for future extension)


class StructuredLogger:
    """Class for structured logging"""

    def __init__(self, logger: Logger, thread_id: str):
        self.logger = logger
        self.thread_id = thread_id

    def _create_log_entry(
        self,
        log_type: LogType,
        data: Dict[str, Any],
        level: LogLevel = LogLevel.INFO,
        node_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create standardized log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value.upper(),
            "log_type": log_type.value,
            "thread_id": self.thread_id,
        }

        if node_name:
            entry["node_name"] = node_name

        entry["data"] = data
        return entry

    def _log(self, entry: Dict[str, Any], level: LogLevel):
        """Actual logging"""
        log_message = json.dumps(entry, ensure_ascii=False, default=serialize)
        getattr(self.logger, level.value)(log_message)

    def log_user_query(
        self, message_content: Any, has_image: bool = False, message_count: int = 1
    ):
        """User query logging"""
        data = {
            "content": message_content,
            "has_image": has_image,
            "message_count": message_count,
        }
        entry = self._create_log_entry(LogType.USER_QUERY, data, LogLevel.INFO)
        self._log(entry, LogLevel.INFO)

    def log_llm_call(
        self,
        template_name: str,
        execution_time_ms: float,
        usage: Dict[str, Any],
        model: str,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """LLM call logging"""
        data = {
            "template_name": template_name,
            "execution_time_ms": round(execution_time_ms, 2),
            "usage": usage,
            "model": model,
        }
        if additional_data:
            data.update(additional_data)

        entry = self._create_log_entry(LogType.LLM_CALL, data, LogLevel.DEBUG)
        self._log(entry, LogLevel.DEBUG)

    def log_node_start(
        self, node_name: str, additional_data: Optional[Dict[str, Any]] = None
    ):
        """Node start logging"""
        data = {"status": "start"}
        if additional_data:
            data.update(additional_data)

        entry = self._create_log_entry(
            LogType.NODE_EXECUTION, data, LogLevel.DEBUG, node_name
        )
        self._log(entry, LogLevel.DEBUG)

    def log_node_end(
        self,
        node_name: str,
        execution_time_ms: Optional[float] = None,
        result_summary: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """Node end logging"""
        data = {"status": "end"}
        if execution_time_ms is not None:
            data["execution_time_ms"] = round(execution_time_ms, 2)
        if result_summary:
            data["result_summary"] = result_summary
        if additional_data:
            data.update(additional_data)

        entry = self._create_log_entry(
            LogType.NODE_EXECUTION, data, LogLevel.INFO, node_name
        )
        self._log(entry, LogLevel.INFO)

    def log_state_change(
        self,
        field: str,
        old_value: Any,
        new_value: Any,
        change_reason: str,
        node_name: Optional[str] = None,
    ):
        """State change logging"""
        data = {
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "change_reason": change_reason,
        }
        entry = self._create_log_entry(
            LogType.STATE_CHANGE, data, LogLevel.DEBUG, node_name
        )
        self._log(entry, LogLevel.DEBUG)

    def log_error(
        self,
        error_type: str,
        error_msg: str,
        node_name: Optional[str] = None,
        filename: Optional[str] = None,
        line: Optional[int] = None,
        model_param: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """Error logging"""
        data = {
            "error_type": error_type,
            "error_msg": error_msg,
        }
        if node_name:
            data["node_name"] = node_name
        if filename:
            data["filename"] = filename
        if line:
            data["line"] = line
        if model_param:
            data["model_param"] = model_param
        if additional_data:
            data.update(additional_data)

        entry = self._create_log_entry(LogType.ERROR, data, LogLevel.ERROR, node_name)
        self._log(entry, LogLevel.ERROR)

    def log_info(self, message: str, additional_data: Optional[Dict[str, Any]] = None):
        """Informational logging"""
        data = {"message": message}
        if additional_data:
            data.update(additional_data)
        entry = self._create_log_entry(LogType.USER_INFO, data, LogLevel.INFO)
        self._log(entry, LogLevel.INFO)

    def log_debug(self, message: str, additional_data: Optional[Dict[str, Any]] = None):
        """Debug logging"""
        data = {"message": message}
        if additional_data:
            data.update(additional_data)
        entry = self._create_log_entry(LogType.NODE_EXECUTION, data, LogLevel.DEBUG)
        self._log(entry, LogLevel.DEBUG)

    def log_warning(
        self, message: str, additional_data: Optional[Dict[str, Any]] = None
    ):
        """Warning logging"""
        data = {"message": message}
        if additional_data:
            data.update(additional_data)
        entry = self._create_log_entry(LogType.NODE_EXECUTION, data, LogLevel.WARNING)
        self._log(entry, LogLevel.WARNING)
