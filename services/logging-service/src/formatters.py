import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class LogContext:
    """Structured context for log entries."""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    resource_id: Optional[str] = None
    operation: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, filtering None values."""
        data = asdict(self)
        filtered = {k: v for k, v in data.items() if v is not None and k != "extra"}
        filtered.update(self.extra)
        return filtered


class PerformanceFormatter:
    """Formatter for performance metrics logging."""

    @staticmethod
    def format_query_log(
        query: str,
        duration_ms: int,
        rows_affected: Optional[int] = None,
        params: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Format database query performance log."""
        return {
            "event": "query_executed",
            "query": query[:300],
            "duration_ms": duration_ms,
            "rows_affected": rows_affected,
            "params_count": len(params) if params else 0,
            "slow": duration_ms > 500,
        }

    @staticmethod
    def format_api_call_log(
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: int,
        response_size_bytes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Format API call performance log."""
        return {
            "event": "api_call",
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "response_size_bytes": response_size_bytes,
            "slow": duration_ms > 1000,
        }


class AuditFormatter:
    """Formatter for audit/compliance logging."""

    @staticmethod
    def format_user_action(
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict[str, Any]] = None,
        status: str = "success",
    ) -> Dict[str, Any]:
        """Format user action for audit trail."""
        return {
            "event": "user_action",
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "changes": changes,
            "status": status,
        }

    @staticmethod
    def format_access_log(
        user_id: str,
        resource: str,
        access_type: str,
        granted: bool,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format access attempt for audit trail."""
        return {
            "event": "access_attempt",
            "user_id": user_id,
            "resource": resource,
            "access_type": access_type,
            "granted": granted,
            "reason": reason,
        }
