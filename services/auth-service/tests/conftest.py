"""Fixtures para testes da Auth Service"""

import os

# Set required env vars BEFORE any src imports
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("ADMIN_USERNAME", "admin@salesforce.com")
os.environ.setdefault("ADMIN_PASSWORD", "secure_password_123")
os.environ.setdefault("ENABLE_DEMO_MODE", "false")

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from src.jwt_handler import JWTHandler
from src.rbac import RBAC
from src.models import UserRole, TokenPayload


@pytest.fixture
def jwt_handler():
    """Fixture para JWTHandler"""
    handler = JWTHandler()
    return handler


@pytest.fixture
def rbac():
    """Fixture para RBAC"""
    return RBAC()


@pytest.fixture
def valid_token():
    """Fixture para token válido"""
    return {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidToxMjM0NSIsInJvbGUiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OTksImlhdCI6MTcyMzgxNjI0NSwicGVybWlzc2lvbnMiOlsicmVwb3J0czpjcmVhdGUiXSwidHlwZSI6ImFjY2VzcyJ9.abcdef123456",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidToxMjM0NSIsImV4cCI6OTk5OTk5OTk5OTksImlhdCI6MTcyMzgxNjI0NSwicHR5cGUiOiJyZWZyZXNoIn0.ghijkl789012",
        "token_type": "bearer",
        "expires_in": 86400
    }


@pytest.fixture
def expired_token():
    """Fixture para token expirado"""
    return {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidToxMjM0NSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxMjM0NTY3ODksImlhdCI6MTcyMzgxNjI0NSwicGVybWlzc2lvbnMiOlsicmVwb3J0czpyZWFkIl0sInR5cGUiOiJhY2Nlc3MifQ.expired",
        "token_type": "bearer"
    }


@pytest.fixture
def token_payload():
    """Fixture para TokenPayload"""
    return TokenPayload(
        user_id="u:12345",
        role=UserRole.ADMIN,
        permissions=["reports:create", "reports:read", "reports:update", "reports:delete"],
        exp=int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        iat=int(datetime.utcnow().timestamp()),
        type="access"
    )


@pytest.fixture
def login_request():
    """Fixture para LoginRequest"""
    return {
        "username": "admin@salesforce.com",
        "password": "secure_password_123"
    }


@pytest.fixture
def mock_db():
    """Mock para banco de dados"""
    mock = Mock()
    mock.query = AsyncMock()
    mock.add = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


@pytest.fixture
def mock_redis():
    """Mock para Redis"""
    mock = AsyncMock()
    mock.get = AsyncMock()
    mock.set = AsyncMock()
    mock.delete = AsyncMock()
    mock.exists = AsyncMock()
    return mock
