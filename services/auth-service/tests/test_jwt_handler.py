"""Tests for JWT handler."""

import pytest
from datetime import timedelta
from src.jwt_handler import JWTHandler, TokenPayload
from jose import JWTError


def test_jwt_handler_create_token():
    """Testar criação de token."""
    handler = JWTHandler(secret_key="test_secret")
    
    token = handler.create_access_token(
        user_id="user123",
        email="user@example.com",
        roles=["admin"]
    )
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_jwt_handler_verify_token():
    """Testar verificação de token."""
    handler = JWTHandler(secret_key="test_secret")
    
    token = handler.create_access_token(
        user_id="user123",
        email="user@example.com",
        roles=["admin"]
    )
    
    payload = handler.verify_token(token)
    
    assert payload.sub == "user123"
    assert payload.email == "user@example.com"
    assert "admin" in payload.roles


def test_jwt_handler_invalid_token():
    """Testar erro com token inválido."""
    handler = JWTHandler(secret_key="test_secret")
    
    with pytest.raises(JWTError):
        handler.verify_token("invalid_token")


def test_jwt_handler_refresh_token():
    """Testar refresh token."""
    handler = JWTHandler(secret_key="test_secret")
    
    refresh_token = handler.create_refresh_token(
        user_id="user123",
        email="user@example.com"
    )
    
    assert isinstance(refresh_token, str)
    
    payload = handler.verify_token(refresh_token)
    assert payload.sub == "user123"
