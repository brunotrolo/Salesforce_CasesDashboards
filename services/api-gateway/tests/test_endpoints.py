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
        json={"username": "admin", "password": "test-password"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials is rejected."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_list_reports_requires_auth(client):
    """Test list reports endpoint requires authentication."""
    response = client.get("/api/reports")

    assert response.status_code == 401


def test_list_reports_with_auth(client, auth_headers):
    """Test list reports with valid token."""
    response = client.get("/api/reports", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data and "total" in data


def test_list_reports_with_limit(client, auth_headers):
    """Test list reports with limit parameter."""
    response = client.get("/api/reports?limit=5", headers=auth_headers)

    assert response.status_code == 200


def test_create_report_structure(client, auth_headers):
    """Test create report endpoint structure."""
    report_data = {
        "name": "Test Report",
        "description": "A test report",
        "object_type": "Case",
        "report_type": "summary",
        "fields": ["Id", "Subject", "Status"]
    }

    response = client.post(
        "/api/reports",
        json=report_data,
        headers=auth_headers
    )

    assert response.status_code in [200, 201, 400]
    if response.status_code in [200, 201]:
        data = response.json()
        assert "report_id" in data or "id" in data


def test_create_report_requires_auth(client):
    """Test create report requires authentication."""
    report_data = {
        "name": "Test Report",
        "object_type": "Case",
        "report_type": "summary",
        "fields": ["Id"]
    }

    response = client.post("/api/reports", json=report_data)

    assert response.status_code == 401


def test_api_404(client):
    """Test 404 error for non-existent endpoint."""
    response = client.get("/api/nonexistent")

    assert response.status_code == 404