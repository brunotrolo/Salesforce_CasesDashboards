import logging
import json
import traceback
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pathlib import Path


class LogLevel(str, Enum):
    """Standard log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Log categories for filtering and analysis."""
    API_REQUEST = "API_REQUEST"
    MCP_OPERATION = "MCP_OPERATION"
    CACHE_OPERATION = "CACHE_OPERATION"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    DATABASE = "DATABASE"
    ERROR = "ERROR"
    SYSTEM = "SYSTEM"


class StructuredLogger:
    """
    Structured logger for JSON-based logging with trace_id and correlation_id.
    Designed for ELK Stack compatibility and production debugging.
    """

    def __init__(
        self,
        service_name: str,
        log_level: LogLevel = LogLevel.INFO,
        log_file: Optional[str] = None,
    ):
        self.service_name = service_name
        self.log_level = log_level
        self.log_file = log_file
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(log_level.value)

        formatter = logging.Formatter(
            fmt='%(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_file:
            log_path = Path(log_file).parent
            log_path.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _format_log(
        self,
        level: LogLevel,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        duration_ms: Optional[int] = None,
    ) -> str:
        """Format log entry as JSON with all metadata."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "level": level.value,
            "category": category.value,
            "trace_id": trace_id or str(uuid.uuid4()),
            "correlation_id": correlation_id or trace_id,
            "message": message,
            "context": context or {},
        }

        if duration_ms is not None:
            log_entry["context"]["duration_ms"] = duration_ms

        if error:
            log_entry["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "stack_trace": traceback.format_exc(),
            }
        else:
            log_entry["error"] = None

        return json.dumps(log_entry)

    def log(
        self,
        level: LogLevel,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        """Generic log method."""
        log_json = self._format_log(
            level=level,
            message=message,
            category=category,
            trace_id=trace_id,
            correlation_id=correlation_id,
            context=context,
            error=error,
            duration_ms=duration_ms,
        )

        log_level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARN: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }

        self.logger.log(log_level_map[level], log_json)

    def debug(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.log(
            LogLevel.DEBUG,
            message,
            category,
            trace_id,
            correlation_id,
            context,
        )

    def info(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        self.log(
            LogLevel.INFO,
            message,
            category,
            trace_id,
            correlation_id,
            context,
            duration_ms=duration_ms,
        )

    def warn(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.log(
            LogLevel.WARN,
            message,
            category,
            trace_id,
            correlation_id,
            context,
        )

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        category: LogCategory = LogCategory.ERROR,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.log(
            LogLevel.ERROR,
            message,
            category,
            trace_id,
            correlation_id,
            context,
            error=error,
        )

    def critical(
        self,
        message: str,
        error: Optional[Exception] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.log(
            LogLevel.CRITICAL,
            message,
            LogCategory.SYSTEM,
            trace_id,
            correlation_id,
            context,
            error=error,
        )

    def log_operation(
        self,
        operation: str,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        """Log a completed operation with optional duration."""
        ctx = context or {}
        ctx["operation"] = operation
        self.info(
            f"Operation completed: {operation}",
            category=LogCategory.API_REQUEST,
            trace_id=trace_id,
            correlation_id=correlation_id,
            context=ctx,
            duration_ms=duration_ms,
        )

    def log_mcp_call(
        self,
        method: str,
        endpoint: str,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        status_code: Optional[int] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        """Log MCP Salesforce API call."""
        context = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
        }
        if duration_ms is not None:
            context["duration_ms"] = duration_ms
        self.debug(
            f"MCP call: {method} {endpoint}",
            category=LogCategory.MCP_OPERATION,
            trace_id=trace_id,
            correlation_id=correlation_id,
            context=context,
        )

    def log_cache_hit(
        self,
        key: str,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Log cache hit."""
        self.debug(
            f"Cache hit: {key}",
            category=LogCategory.CACHE_OPERATION,
            trace_id=trace_id,
            correlation_id=correlation_id,
            context={"key": key, "hit": True},
        )

    def log_cache_miss(
        self,
        key: str,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Log cache miss."""
        self.debug(
            f"Cache miss: {key}",
            category=LogCategory.CACHE_OPERATION,
            trace_id=trace_id,
            correlation_id=correlation_id,
            context={"key": key, "hit": False},
        )

    def log_security_event(
        self,
        event: str,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log security-relevant event (e.g., unauthorized access)."""
        ctx = context or {}
        if user_id:
            ctx["user_id"] = user_id
        self.warn(
            event,
            category=LogCategory.SECURITY,
            trace_id=trace_id,
            correlation_id=correlation_id,
            context=ctx,
        )

    def log_slow_query(
        self,
        query: str,
        duration_ms: int,
        threshold_ms: int = 500,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Log queries exceeding performance threshold."""
        if duration_ms > threshold_ms:
            self.info(
                f"Slow query detected: {duration_ms}ms > {threshold_ms}ms",
                category=LogCategory.PERFORMANCE,
                trace_id=trace_id,
                correlation_id=correlation_id,
                context={
                    "query": query[:200],
                    "duration_ms": duration_ms,
                    "threshold_ms": threshold_ms,
                },
                duration_ms=duration_ms,
            )
