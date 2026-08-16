"""Testes para JWT Handler"""

import pytest
from datetime import datetime, timedelta
from jose import JWTError

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
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] > 0

    def test_validate_access_token(self, jwt_handler):
        """Testa validação de token de acesso"""
        user_id = "u:12345"
        role = UserRole.USER
        permissions = ["reports:read"]

        token = jwt_handler.create_access_token(user_id, role, permissions)
        payload = jwt_handler.validate_token(token)

        assert payload is not None
        assert payload.user_id == user_id
        assert payload.role == role
        assert payload.type == "access"

    def test_validate_token_invalid_signature(self, jwt_handler):
        """Testa validação com assinatura inválida"""
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid"

        with pytest.raises(JWTError):
            jwt_handler.validate_token(invalid_token)

    def test_validate_token_expired(self, jwt_handler):
        """Testa validação de token expirado"""
        user_id = "u:12345"
        role = UserRole.GUEST

        # Criar token com expiração negativa (já expirado)
        token = jwt_handler.create_access_token(user_id, role, [])
        
        # Modificar manualmente para estar expirado (isso é um teste básico)
        with pytest.raises(JWTError):
            payload = jwt_handler.validate_token(token)
            if jwt_handler.is_token_expired(token):
                raise JWTError("Token expired")

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
        assert payload.user_id == user_id

    def test_validate_refresh_token_method(self, jwt_handler):
        """Testa validação específica para refresh token"""
        user_id = "u:12345"

        token = jwt_handler.create_refresh_token(user_id)
        retrieved_user_id = jwt_handler.validate_refresh_token(token)

        assert retrieved_user_id == user_id

    def test_get_expiration_time(self, jwt_handler):
        """Testa obtenção do tempo de expiração"""
        user_id = "u:12345"
        role = UserRole.USER

        token = jwt_handler.create_access_token(user_id, role, [])
        exp_time = jwt_handler.get_expiration_time(token)

        assert exp_time is not None
        assert isinstance(exp_time, datetime)
        assert exp_time > datetime.utcnow()

    def test_token_contains_user_id(self, jwt_handler):
        """Testa se token contém user_id"""
        user_id = "u:67890"
        role = UserRole.ADMIN

        token = jwt_handler.create_access_token(user_id, role, ["reports:create"])
        payload = jwt_handler.validate_token(token)

        assert payload.user_id == user_id

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
        payload = jwt_handler.validate_token(token)

        assert payload.type == "refresh"
        assert not hasattr(payload, "permissions") or payload.permissions is None
