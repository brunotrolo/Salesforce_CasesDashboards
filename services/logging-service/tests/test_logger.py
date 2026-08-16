import pytest
import json
import logging
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import (
    StructuredLogger,
    LogLevel,
    LogCategory,
)


@pytest.fixture
def temp_log_file():
    """Create temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def logger(temp_log_file):
    """Create structured logger instance."""
    return StructuredLogger(
        service_name="test-service",
        log_level=LogLevel.DEBUG,
        log_file=temp_log_file,
    )


class TestStructuredLogger:
    def test_logger_initialization(self, logger):
        """Test logger is properly initialized."""
        assert logger.service_name == "test-service"
        assert logger.log_level == LogLevel.DEBUG
        assert logger.logger is not None

    def test_debug_logging(self, logger, caplog):
        """Test debug level logging."""
        with caplog.at_level(logging.DEBUG):
            logger.debug(
                "Debug message",
                category=LogCategory.SYSTEM,
                context={"key": "value"},
            )

        assert len(caplog.records) > 0
        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["level"] == "DEBUG"
        assert log_entry["message"] == "Debug message"
        assert log_entry["service"] == "test-service"
        assert log_entry["context"]["key"] == "value"

    def test_info_logging(self, logger, caplog):
        """Test info level logging."""
        with caplog.at_level(logging.INFO):
            logger.info(
                "Info message",
                category=LogCategory.API_REQUEST,
                context={"operation": "create"},
                duration_ms=100,
            )

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["level"] == "INFO"
        assert log_entry["category"] == "API_REQUEST"
        assert log_entry["context"]["duration_ms"] == 100

    def test_error_logging_with_exception(self, logger, caplog):
        """Test error logging with exception details."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            with caplog.at_level(logging.ERROR):
                logger.error(
                    "Operation failed",
                    error=e,
                    category=LogCategory.ERROR,
                )

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["level"] == "ERROR"
        assert log_entry["error"]["type"] == "ValueError"
        assert log_entry["error"]["message"] == "Test error"
        assert "stack_trace" in log_entry["error"]

    def test_trace_id_generation(self, logger, caplog):
        """Test trace_id is generated if not provided."""
        with caplog.at_level(logging.INFO):
            logger.info("Message without trace_id")

        log_entry = json.loads(caplog.records[0].message)
        assert "trace_id" in log_entry
        assert log_entry["trace_id"] is not None
        assert len(log_entry["trace_id"]) > 0

    def test_trace_id_preservation(self, logger, caplog):
        """Test trace_id is preserved when provided."""
        trace_id = "test-trace-123"
        with caplog.at_level(logging.INFO):
            logger.info("Message with trace_id", trace_id=trace_id)

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["trace_id"] == trace_id

    def test_correlation_id_defaults_to_trace_id(self, logger, caplog):
        """Test correlation_id defaults to trace_id."""
        trace_id = "test-trace-456"
        with caplog.at_level(logging.INFO):
            logger.info("Message", trace_id=trace_id)

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["correlation_id"] == trace_id

    def test_correlation_id_separate_from_trace_id(self, logger, caplog):
        """Test correlation_id can be different from trace_id."""
        trace_id = "trace-789"
        correlation_id = "correlation-456"
        with caplog.at_level(logging.INFO):
            logger.info(
                "Message",
                trace_id=trace_id,
                correlation_id=correlation_id,
            )

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["trace_id"] == trace_id
        assert log_entry["correlation_id"] == correlation_id

    def test_log_operation(self, logger, caplog):
        """Test operation logging helper."""
        with caplog.at_level(logging.INFO):
            logger.log_operation(
                operation="create_report",
                context={"report_id": "r:123"},
                duration_ms=250,
            )

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["category"] == "API_REQUEST"
        assert log_entry["context"]["operation"] == "create_report"
        assert log_entry["context"]["duration_ms"] == 250

    def test_log_mcp_call(self, logger, caplog):
        """Test MCP call logging."""
        with caplog.at_level(logging.DEBUG):
            logger.log_mcp_call(
                method="POST",
                endpoint="/services/data/v60.0/sobjects/Report",
                status_code=201,
                duration_ms=500,
            )

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["category"] == "MCP_OPERATION"
        assert log_entry["context"]["method"] == "POST"
        assert log_entry["context"]["status_code"] == 201

    def test_log_cache_hit(self, logger, caplog):
        """Test cache hit logging."""
        with caplog.at_level(logging.DEBUG):
            logger.log_cache_hit(key="report:123")

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["category"] == "CACHE_OPERATION"
        assert log_entry["context"]["key"] == "report:123"
        assert log_entry["context"]["hit"] is True

    def test_log_cache_miss(self, logger, caplog):
        """Test cache miss logging."""
        with caplog.at_level(logging.DEBUG):
            logger.log_cache_miss(key="report:456")

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["category"] == "CACHE_OPERATION"
        assert log_entry["context"]["hit"] is False

    def test_log_security_event(self, logger, caplog):
        """Test security event logging."""
        with caplog.at_level(logging.WARNING):
            logger.log_security_event(
                event="Unauthorized access attempt",
                user_id="u:789",
                context={"resource": "/api/reports"},
            )

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["level"] == "WARN"
        assert log_entry["category"] == "SECURITY"
        assert log_entry["context"]["user_id"] == "u:789"

    def test_log_slow_query(self, logger, caplog):
        """Test slow query detection and logging."""
        with caplog.at_level(logging.INFO):
            logger.log_slow_query(
                query="SELECT * FROM reports WHERE...",
                duration_ms=1200,
                threshold_ms=500,
            )

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["level"] == "INFO"
        assert log_entry["category"] == "PERFORMANCE"
        assert log_entry["context"]["duration_ms"] == 1200

    def test_slow_query_under_threshold_not_logged(self, logger, caplog):
        """Test that queries under threshold are not logged."""
        with caplog.at_level(logging.INFO):
            logger.log_slow_query(
                query="SELECT * FROM reports WHERE id=1",
                duration_ms=100,
                threshold_ms=500,
            )

        assert len(caplog.records) == 0

    def test_timestamp_format(self, logger, caplog):
        """Test ISO 8601 timestamp format with Z suffix."""
        with caplog.at_level(logging.INFO):
            logger.info("Message")

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["timestamp"].endswith("Z")
        assert "T" in log_entry["timestamp"]

    def test_context_dict_structure(self, logger, caplog):
        """Test context is properly structured in log entry."""
        context = {
            "user_id": "u:123",
            "report_id": "r:456",
            "action": "update",
        }
        with caplog.at_level(logging.INFO):
            logger.info("Complex operation", context=context)

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["context"]["user_id"] == "u:123"
        assert log_entry["context"]["report_id"] == "r:456"
        assert log_entry["context"]["action"] == "update"
