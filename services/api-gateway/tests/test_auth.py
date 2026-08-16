"""Tests for authentication endpoints."""

import pytest


def test_login_endpoint(client):
    """Test login endpoint."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "password"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_empty_credentials(client):
    """Test login with empty credentials."""
    response = client.post(
        "/auth/login",
        json={"username": "", "password": ""}
    )

    assert response.status_code == 400


def test_auth_token_endpoint(client):
    """Test token endpoint."""
    response = client.post(
        "/auth/token",
        json={"username": "testuser", "password": "testpass"}
    )

    assert response.status_code in [200, 400]
