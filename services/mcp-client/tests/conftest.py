import pytest
import os
from datetime import datetime, timedelta

os.environ.setdefault("SF_CLIENT_ID", "test_client_id")
os.environ.setdefault("SF_CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("SF_INSTANCE_URL", "https://test.salesforce.com")
os.environ.setdefault("SF_REDIRECT_URI", "http://localhost:3005/oauth/callback")

from src.config import settings
from src.oauth_handler import OAuthHandler
from src.models import OAuthToken

@pytest.fixture
def oauth_handler():
    """Fixture para OAuthHandler."""
    return OAuthHandler()

@pytest.fixture
def mock_token():
    """Fixture para mock token."""
    return OAuthToken(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        token_type="Bearer",
        expires_in=3600,
        expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat(),
    )

@pytest.fixture
def mock_salesforce_env(monkeypatch):
    """Fixture para configurações mock do Salesforce."""
    monkeypatch.setenv("SF_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SF_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("SF_INSTANCE_URL", "https://test.salesforce.com")
    monkeypatch.setenv("SF_REDIRECT_URI", "http://localhost:3005/oauth/callback")
