"""Testes para JWT Handler"""

import pytest
from datetime import datetime, timedelta, timezone
import jwt

from src.jwt_handler import JWTHandler
from src.models import UserRole


class TestJWTHandler:
    """Suite de testes para JWTHandler"""

    def test_create_access_token(self, jwt_handler):
        """Testa criação de token de acesso"""
        user_id = "u:12345"
        role = UserRole.ADMIN
        permissions = ["reports:create", "reports:read"]

        token = jwt_handler.create_access_token(user_id, role, permissions)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, jwt_handler):
        """Testa criação de token de refresh"""
        user_id = "u:12345"

        token = jwt_handler.create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_pair(self, jwt_handler):
        """Testa criação de par de tokens"""
        user_id = "u:12345"
        role = UserRole.MANAGER
        permissions = ["reports:read", "reports:execute"]

        tokens = jwt_handler.create_token_pair(user_id, role, permissions)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "Bearer"
        assert tokens["expires_in"] > 0

    def test_validate_access_token(self, jwt_handler):
        """Testa validação de token de acesso"""
        user_id = "u:12345"
        role = UserRole.USER
        permissions = ["reports:read"]

        token = jwt_handler.create_access_token(user_id, role, permissions)
        payload = jwt_handler.validate_token(token)

        assert payload is not None
        assert payload.sub == user_id
        assert payload.role == role
        assert payload.type.value == "access"

    def test_validate_token_invalid_signature(self, jwt_handler):
        """Testa validação com assinatura inválida"""
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid"

        payload = jwt_handler.validate_token(invalid_token)

        assert payload is None

    def test_validate_token_expired(self, jwt_handler):
        """Testa validação de token expirado"""
        # Criar token com expiração no passado (timestamp absoluto de 2023)
        expired_payload = {
            "sub": "u:12345",
            "exp": 1700000000,
            "iat": 1699996400,
            "type": "access",
            "role": UserRole.USER.value,
            "permissions": [],
        }
        token = jwt.encode(
            expired_payload,
            jwt_handler.secret_key,
            algorithm=jwt_handler.algorithm,
        )

        assert jwt_handler.validate_token(token) is None
        assert jwt_handler.is_token_expired(token) is True

    def test_is_token_expired_valid_token(self, jwt_handler):
        """Testa se token válido não está expirado"""
        user_id = "u:12345"
        role = UserRole.ADMIN

        token = jwt_handler.create_access_token(user_id, role, [])

        assert not jwt_handler.is_token_expired(token)

    def test_validate_access_token_method(self, jwt_handler):
        """Testa validação específica para access token"""
        user_id = "u:12345"
        role = UserRole.MANAGER

        token = jwt_handler.create_access_token(user_id, role, [])
        payload = jwt_handler.validate_access_token(token)

        assert payload is not None
        assert payload.sub == user_id

    def test_validate_refresh_token_method(self, jwt_handler):
        """Testa validação específica para refresh token"""
        user_id = "u:12345"

        token = jwt_handler.create_refresh_token(user_id)
        retrieved_user_id = jwt_handler.validate_refresh_token(token)

        assert retrieved_user_id == user_id

    def test_validate_access_token_rejects_refresh_token(self, jwt_handler):
        """Testa que refresh token não é aceito como access token"""
        user_id = "u:12345"

        token = jwt_handler.create_refresh_token(user_id)

        assert jwt_handler.validate_access_token(token) is None

    def test_get_expiration_time(self, jwt_handler):
        """Testa obtenção do tempo de expiração"""
        user_id = "u:12345"
        role = UserRole.USER

        token = jwt_handler.create_access_token(user_id, role, [])
        exp_time = jwt_handler.get_expiration_time(token)

        assert exp_time is not None
        assert isinstance(exp_time, datetime)
        assert exp_time > datetime.now(timezone.utc)

    def test_token_contains_user_id(self, jwt_handler):
        """Testa se token contém user_id"""
        user_id = "u:67890"
        role = UserRole.ADMIN

        token = jwt_handler.create_access_token(user_id, role, ["reports:create"])
        payload = jwt_handler.validate_token(token)

        assert payload.sub == user_id

    def test_token_contains_role(self, jwt_handler):
        """Testa se token contém role"""
        user_id = "u:12345"
        role = UserRole.MANAGER

        token = jwt_handler.create_access_token(user_id, role, [])
        payload = jwt_handler.validate_token(token)

        assert payload.role == role

    def test_token_contains_permissions(self, jwt_handler):
        """Testa se token contém permissions"""
        user_id = "u:12345"
        role = UserRole.ADMIN
        permissions = ["reports:create", "reports:read", "users:read"]

        token = jwt_handler.create_access_token(user_id, role, permissions)
        payload = jwt_handler.validate_token(token)

        assert set(payload.permissions) == set(permissions)

    def test_refresh_token_doesnt_contain_permissions(self, jwt_handler):
        """Testa se refresh token não contém permissions"""
        user_id = "u:12345"

        token = jwt_handler.create_refresh_token(user_id)
        raw_payload = jwt.decode(
            token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm]
        )

        assert raw_payload["type"] == "refresh"
        assert "permissions" not in raw_payload
        assert jwt_handler.validate_access_token(token) is None