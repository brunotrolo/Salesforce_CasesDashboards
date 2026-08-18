import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.formatters import (
    LogContext,
    PerformanceFormatter,
    AuditFormatter,
)


class TestLogContext:
    def test_log_context_initialization(self):
        """Test LogContext initialization."""
        ctx = LogContext(
            user_id="u:123",
            request_id="req:456",
            operation="create",
        )
        assert ctx.user_id == "u:123"
        assert ctx.request_id == "req:456"
        assert ctx.operation == "create"

    def test_log_context_to_dict(self):
        """Test converting LogContext to dict."""
        ctx = LogContext(
            user_id="u:789",
            operation="update",
        )
        data = ctx.to_dict()
        assert data["user_id"] == "u:789"
        assert data["operation"] == "update"

    def test_log_context_filters_none_values(self):
        """Test None values are filtered from dict."""
        ctx = LogContext(
            user_id="u:123",
            request_id=None,
            operation="read",
        )
        data = ctx.to_dict()
        assert "user_id" in data
        assert "request_id" not in data
        assert "operation" in data

    def test_log_context_includes_extra(self):
        """Test extra fields are included in dict."""
        ctx = LogContext(
            user_id="u:123",
            extra={"custom_field": "custom_value"},
        )
        data = ctx.to_dict()
        assert data["custom_field"] == "custom_value"

    def test_log_context_empty_extra_by_default(self):
        """Test empty extra dict by default."""
        ctx = LogContext()
        data = ctx.to_dict()
        assert isinstance(data, dict)


class TestPerformanceFormatter:
    def test_format_query_log(self):
        """Test formatting database query log."""
        result = PerformanceFormatter.format_query_log(
            query="SELECT * FROM reports WHERE id=?",
            duration_ms=250,
            rows_affected=1,
            params=[123],
        )
        assert result["event"] == "query_executed"
        assert result["query"] == "SELECT * FROM reports WHERE id=?"
        assert result["duration_ms"] == 250
        assert result["rows_affected"] == 1
        assert result["params_count"] == 1
        assert result["slow"] is False

    def test_format_query_log_marks_slow(self):
        """Test slow queries are marked."""
        result = PerformanceFormatter.format_query_log(
            query="SELECT * FROM large_table",
            duration_ms=1500,
        )
        assert result["slow"] is True

    def test_format_query_log_truncates_long_query(self):
        """Test long queries are truncated."""
        long_query = "SELECT " + "field, " * 100 + "FROM table"
        result = PerformanceFormatter.format_query_log(
            query=long_query,
            duration_ms=100,
        )
        assert len(result["query"]) <= 300

    def test_format_api_call_log(self):
        """Test formatting API call log."""
        result = PerformanceFormatter.format_api_call_log(
            method="POST",
            endpoint="/api/reports",
            status_code=201,
            duration_ms=450,
            response_size_bytes=2048,
        )
        assert result["event"] == "api_call"
        assert result["method"] == "POST"
        assert result["endpoint"] == "/api/reports"
        assert result["status_code"] == 201
        assert result["response_size_bytes"] == 2048
        assert result["slow"] is False

    def test_format_api_call_marks_slow(self):
        """Test slow API calls are marked."""
        result = PerformanceFormatter.format_api_call_log(
            method="GET",
            endpoint="/api/reports/search",
            status_code=200,
            duration_ms=2000,
        )
        assert result["slow"] is True


class TestAuditFormatter:
    def test_format_user_action(self):
        """Test formatting user action for audit."""
        result = AuditFormatter.format_user_action(
            user_id="u:123",
            action="create",
            resource_type="Report",
            resource_id="r:456",
            changes={"name": "New Report"},
            status="success",
        )
        assert result["event"] == "user_action"
        assert result["user_id"] == "u:123"
        assert result["action"] == "create"
        assert result["resource_type"] == "Report"
        assert result["resource_id"] == "r:456"
        assert result["changes"] == {"name": "New Report"}
        assert result["status"] == "success"

    def test_format_user_action_no_changes(self):
        """Test user action without changes."""
        result = AuditFormatter.format_user_action(
            user_id="u:789",
            action="delete",
            resource_type="Report",
            resource_id="r:789",
        )
        assert result["changes"] is None

    def test_format_access_log_granted(self):
        """Test formatting granted access attempt."""
        result = AuditFormatter.format_access_log(
            user_id="u:111",
            resource="/api/reports/123",
            access_type="read",
            granted=True,
        )
        assert result["event"] == "access_attempt"
        assert result["user_id"] == "u:111"
        assert result["resource"] == "/api/reports/123"
        assert result["access_type"] == "read"
        assert result["granted"] is True

    def test_format_access_log_denied(self):
        """Test formatting denied access attempt."""
        result = AuditFormatter.format_access_log(
            user_id="u:222",
            resource="/api/admin",
            access_type="write",
            granted=False,
            reason="Insufficient permissions",
        )
        assert result["event"] == "access_attempt"
        assert result["granted"] is False
        assert result["reason"] == "Insufficient permissions"
