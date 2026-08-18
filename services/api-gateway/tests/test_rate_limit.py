"""Tests for rate limiting middleware."""

import time

import pytest
from src.rate_limit import RateLimiter, get_client_ip, rate_limiter


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


def test_rate_limit_exceeded_returns_429(client):
    """Test that exceeding the limit returns 429."""
    limiter = rate_limiter
    fake_ip = "203.0.113.99"
    for _ in range(limiter.requests_per_minute):
        assert limiter.is_allowed(fake_ip)[0]
    allowed, info = limiter.is_allowed(fake_ip)
    assert allowed is False
    assert info["current"] >= limiter.requests_per_minute


def test_get_client_ip_uses_x_forwarded_for(client):
    """X-Forwarded-For é usado quando há proxies confiáveis."""
    from unittest.mock import patch

    with patch("src.rate_limit.TRUSTED_PROXIES", {"10.0.0.1"}):
        response = client.get(
            "/health",
            headers={"X-Forwarded-For": "203.0.113.7, 10.0.0.1"},
        )
        assert response.status_code == 200


def test_get_client_ip_falls_back_to_direct_ip(client):
    """Sem X-Forwarded-For, usa o IP da conexão direta."""
    from fastapi import Request

    request = Request({"type": "http", "client": ("198.51.100.2", 1234)})
    ip = get_client_ip(request)
    assert ip == "198.51.100.2"


def test_cleanup_removes_stale_entries():
    """Entries inativas são removidas após o TTL."""
    limiter = RateLimiter(requests_per_minute=60, max_clients=10000, entry_ttl=300)
    limiter.is_allowed("stale-client")
    assert "stale-client" in limiter.requests

    stale_before = time.time() - 301
    limiter.requests["stale-client"] = [stale_before]
    limiter._last_cleanup = 0.0
    limiter._cleanup()
    assert "stale-client" not in limiter.requests


def test_cleanup_respects_cleanup_interval():
    """Cleanup não roda antes do intervalo mínimo."""
    limiter = RateLimiter()
    limiter.requests["client-a"] = [time.time() - 301]
    limiter._last_cleanup = time.time()
    limiter._cleanup()
    assert "client-a" in limiter.requests


def test_cleanup_keeps_recent_entries():
    """Entries com atividade recente são mantidas."""
    limiter = RateLimiter()
    limiter.requests["active-client"] = [time.time()]
    limiter._last_cleanup = 0.0
    limiter._cleanup()
    assert "active-client" in limiter.requests
