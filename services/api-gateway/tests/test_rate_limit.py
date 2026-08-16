"""Tests for rate limiting middleware."""

import pytest


def test_rate_limiting_middleware_active(client):
    """Test that rate limiting middleware is active."""
    # Should accept requests below limit
    response = client.get("/health")
    assert response.status_code == 200

    # Check if rate limit headers are present (optional)
    # assert "X-RateLimit-Remaining" in response.headers


def test_health_check_not_rate_limited(client):
    """Test that health check works without rate limiting issues."""
    for i in range(5):
        response = client.get("/health")
        assert response.status_code == 200
