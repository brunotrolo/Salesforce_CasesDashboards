"""Tests for API Gateway endpoints."""

import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"


def test_login(client):
    """Test login endpoint."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "password"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_list_reports_without_auth(client):
    """Test list reports endpoint without authentication."""
    response = client.get("/api/reports")

    # Should return 200 for dev mode
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        data = response.json()
        assert "reports" in data or "data" in data


def test_list_reports_with_limit(client):
    """Test list reports with limit parameter."""
    response = client.get("/api/reports?limit=5")

    assert response.status_code in [200, 401]


def test_create_report_structure(client):
    """Test create report endpoint structure."""
    report_data = {
        "title": "Test Report",
        "description": "A test report",
        "config": {"type": "test"}
    }

    response = client.post(
        "/api/reports",
        json=report_data
    )

    # Should return 200, 201, or 401 (if auth required)
    assert response.status_code in [200, 201, 401]
    if response.status_code in [200, 201]:
        data = response.json()
        assert "id" in data or "report_id" in data


def test_api_404(client):
    """Test 404 error for non-existent endpoint."""
    response = client.get("/api/nonexistent")

    assert response.status_code == 404
