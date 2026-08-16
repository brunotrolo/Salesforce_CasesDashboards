import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from starlette.testclient import TestClient
from fastapi import FastAPI, Request

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.middleware import LoggingMiddleware, ContextVars
from src.logger import StructuredLogger, LogLevel


@pytest.fixture
def app():
    """Create FastAPI test app with logging middleware."""
    app = FastAPI()
    logger = StructuredLogger("test-api", log_level=LogLevel.DEBUG)
    app.add_middleware(LoggingMiddleware, logger=logger)

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    @app.post("/create")
    async def create_endpoint(request: Request):
        trace_id = request.state.trace_id
        correlation_id = request.state.correlation_id
        return {
            "trace_id": trace_id,
            "correlation_id": correlation_id,
        }

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestLoggingMiddleware:
    def test_middleware_injects_trace_id(self, client, caplog):
        """Test middleware injects trace_id header."""
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-Trace-ID" in response.headers

    def test_middleware_preserves_provided_trace_id(self, client):
        """Test middleware preserves provided trace_id."""
        trace_id = "provided-trace-123"
        response = client.get(
            "/test",
            headers={"X-Trace-ID": trace_id},
        )
        assert response.status_code == 200
        assert response.headers.get("X-Trace-ID") == trace_id

    def test_middleware_injects_correlation_id(self, client):
        """Test middleware injects correlation_id header."""
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers

    def test_middleware_sets_correlation_id_from_trace_id(self, client):
        """Test correlation_id defaults to trace_id."""
        trace_id = "test-trace-789"
        response = client.get(
            "/test",
            headers={"X-Trace-ID": trace_id},
        )
        assert response.headers.get("X-Correlation-ID") == trace_id

    def test_middleware_preserves_separate_correlation_id(self, client):
        """Test separate correlation_id is preserved."""
        trace_id = "trace-111"
        correlation_id = "correlation-222"
        response = client.get(
            "/test",
            headers={
                "X-Trace-ID": trace_id,
                "X-Correlation-ID": correlation_id,
            },
        )
        assert response.headers.get("X-Trace-ID") == trace_id
        assert response.headers.get("X-Correlation-ID") == correlation_id

    def test_middleware_available_in_request_state(self, client):
        """Test trace_id and correlation_id available in request.state."""
        response = client.post("/create")
        data = response.json()
        assert "trace_id" in data
        assert "correlation_id" in data
        assert len(data["trace_id"]) > 0

    def test_middleware_logs_successful_request(self, client, caplog):
        """Test middleware logs successful requests."""
        with caplog.at_level("INFO"):
            response = client.get("/test")

        assert response.status_code == 200
        assert len(caplog.records) > 0
        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["message"] == "GET /test"
        assert log_entry["context"]["status_code"] == 200
        assert "duration_ms" in log_entry["context"]

    def test_middleware_logs_error_request(self, client, caplog):
        """Test middleware logs failed requests."""
        with caplog.at_level("ERROR"):
            try:
                response = client.get("/error")
            except ValueError:
                pass

        assert len(caplog.records) > 0
        log_entry = json.loads(caplog.records[0].message)
        assert "failed" in log_entry["message"].lower()

    def test_middleware_records_duration(self, client, caplog):
        """Test middleware records request duration."""
        with caplog.at_level("INFO"):
            response = client.get("/test")

        log_entry = json.loads(caplog.records[0].message)
        assert "duration_ms" in log_entry["context"]
        assert log_entry["context"]["duration_ms"] >= 0

    def test_middleware_logs_request_method(self, client, caplog):
        """Test middleware logs request method."""
        with caplog.at_level("INFO"):
            response = client.post("/create")

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["context"]["method"] == "POST"

    def test_middleware_logs_path(self, client, caplog):
        """Test middleware logs request path."""
        with caplog.at_level("INFO"):
            response = client.get("/test")

        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["context"]["path"] == "/test"


class TestContextVars:
    def test_set_and_get_trace_id(self):
        """Test setting and getting trace_id."""
        trace_id = "test-123"
        ContextVars.set_trace_id(trace_id)
        assert ContextVars.get_trace_id() == trace_id

    def test_get_trace_id_generates_uuid_if_not_set(self):
        """Test trace_id is generated if not set."""
        ContextVars.clear()
        trace_id = ContextVars.get_trace_id()
        assert trace_id is not None
        assert len(trace_id) > 0

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation_id."""
        correlation_id = "correlation-456"
        ContextVars.set_correlation_id(correlation_id)
        assert ContextVars.get_correlation_id() == correlation_id

    def test_correlation_id_defaults_to_trace_id(self):
        """Test correlation_id defaults to trace_id."""
        ContextVars.clear()
        trace_id = "trace-789"
        ContextVars.set_trace_id(trace_id)
        assert ContextVars.get_correlation_id() == trace_id

    def test_clear_context(self):
        """Test clearing context vars."""
        ContextVars.set_trace_id("trace")
        ContextVars.set_correlation_id("correlation")
        ContextVars.clear()

        new_trace_id = ContextVars.get_trace_id()
        assert new_trace_id != "trace"
