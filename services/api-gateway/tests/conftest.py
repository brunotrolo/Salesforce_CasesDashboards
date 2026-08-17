"""Test configuration for API Gateway."""

import pytest
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import json
from datetime import datetime, timedelta, timezone

# Ensure services directory is in path for relative imports
services_dir = Path(__file__).parent.parent.parent
if str(services_dir) not in sys.path:
    sys.path.insert(0, str(services_dir))

api_gateway_src = Path(__file__).parent.parent / "src"
if str(api_gateway_src) not in sys.path:
    sys.path.insert(0, str(api_gateway_src))

# Set environment variables BEFORE any imports
os.environ.setdefault("SF_CLIENT_ID", "test")
os.environ.setdefault("SF_CLIENT_SECRET", "test")
os.environ.setdefault("SF_REFRESH_TOKEN", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")


@pytest.fixture(scope="session", autouse=True)
def mock_jwt_globally():
    """Mock jwt module globally before any imports."""
    mock_jwt = MagicMock()

    def mock_encode(payload, key, algorithm="HS256"):
        # Simulate JWT encoding
        import base64
        token_data = base64.b64encode(json.dumps(payload).encode()).decode()
        return f"test.{token_data}.signature"

    def mock_decode(token, key, algorithms=None):
        # Simulate JWT decoding
        return {
            "sub": "testuser",
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }

    mock_jwt.encode = mock_encode
    mock_jwt.decode = mock_decode
    mock_jwt.ExpiredSignatureError = Exception
    mock_jwt.InvalidTokenError = Exception

    with patch.dict('sys.modules', {'jwt': mock_jwt}):
        yield


@pytest.fixture
def client():
    """Create a test client for the API."""
    from main import app
    # Use context manager to ensure lifespan is properly called
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers():
    """Headers with a valid (mocked) bearer token."""
    return {"Authorization": "Bearer test-token"}
