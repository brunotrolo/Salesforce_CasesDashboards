"""Testes para endpoints da Auth Service"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.main import app
from src.models import UserRole


client = TestClient(app)


class TestAuthEndpoints:
    """Suite de testes para endpoints de autenticação"""

    def test_health_check(self):
        """Testa endpoint de health check"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth-service"

    def test_readiness_probe(self):
        """Testa endpoint de readiness probe"""
        response = client.get("/health/readiness")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    @patch("src.main.jwt_handler")
    def test_login_success(self, mock_jwt):
        """Testa login bem-sucedido"""
        mock_jwt.create_token_pair.return_value = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "token_type": "Bearer",
            "expires_in": 86400
        }

        response = client.post(
            "/auth/login",
            json={"username": "admin@salesforce.com", "password": "secure_password_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

    def test_login_missing_credentials(self):
        """Testa login sem credenciais"""
        response = client.post("/auth/login", json={})

        assert response.status_code == 422  # Unprocessable Entity

    def test_login_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        response = client.post(
            "/auth/login",
            json={"username": "invalid@example.com", "password": "wrong_password"}
        )

        assert response.status_code == 401

    @patch("src.main.jwt_handler")
    def test_refresh_token(self, mock_jwt):
        """Testa refresh de token"""
        mock_jwt.validate_refresh_token.return_value = "u:12345"
        mock_jwt.create_token_pair.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "Bearer",
            "expires_in": 86400
        }

        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "mock_refresh_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @patch("src.main.jwt_handler")
    def test_get_current_user(self, mock_jwt):
        """Testa obtenção do usuário atual"""
        mock_payload = MagicMock()
        mock_payload.sub = "u:12345"
        mock_payload.role = UserRole.ADMIN
        mock_payload.permissions = ["reports:read", "reports:create"]
        mock_payload.iat = 1700000000

        mock_jwt.validate_access_token.return_value = mock_payload

        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer mock_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "u:12345"
        assert data["username"] == "12345"

    @patch("src.main.jwt_handler")
    def test_get_permissions(self, mock_jwt):
        """Testa obtenção de permissões do usuário"""
        mock_payload = MagicMock()
        mock_payload.sub = "u:12345"
        mock_payload.role = UserRole.ADMIN
        mock_payload.permissions = ["reports:read", "reports:create"]

        mock_jwt.validate_access_token.return_value = mock_payload

        response = client.get(
            "/auth/permissions",
            headers={"Authorization": "Bearer mock_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "reports:read" in data
        assert "reports:create" in data

    def test_get_roles(self):
        """Testa obtenção de papéis disponíveis"""
        response = client.get("/auth/roles")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        role_names = [r["name"] for r in data]
        assert "admin" in role_names
        assert "guest" in role_names

    @patch("src.main.jwt_handler")
    def test_validate_token_valid(self, mock_jwt):
        """Testa validação de token válido"""
        mock_payload = MagicMock()
        mock_payload.sub = "u:12345"
        mock_payload.role = UserRole.ADMIN
        mock_jwt.validate_access_token.return_value = mock_payload

        response = client.post(
            "/auth/validate-token",
            headers={"X-Token": "valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["user_id"] == "u:12345"

    @patch("src.main.jwt_handler")
    def test_check_permission(self, mock_jwt):
        """Testa verificação de permissão"""
        mock_payload = MagicMock()
        mock_payload.sub = "u:12345"
        mock_payload.role = UserRole.ADMIN
        mock_payload.permissions = ["reports:create"]

        mock_jwt.validate_access_token.return_value = mock_payload

        response = client.post(
            "/auth/permissions/reports/create",
            headers={"Authorization": "Bearer mock_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["granted"] is True

    @patch("src.main.jwt_handler")
    def test_logout(self, mock_jwt):
        """Testa logout"""
        mock_payload = MagicMock()
        mock_payload.sub = "u:12345"
        mock_payload.role = UserRole.ADMIN

        mock_jwt.validate_access_token.return_value = mock_payload

        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer mock_token"}
        )

        assert response.status_code == 200


class TestErrorHandling:
    """Testes para tratamento de erros"""

    def test_invalid_endpoint(self):
        """Testa endpoint inválido"""
        response = client.get("/api/nonexistent")

        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Testa método não permitido"""
        response = client.get("/auth/login")  # POST esperado

        assert response.status_code == 405

    def test_missing_authorization_header(self):
        """Testa falta de header de autorização"""
        response = client.get("/auth/me")

        assert response.status_code == 401

    @patch("src.main.jwt_handler")
    def test_invalid_token_format(self, mock_jwt):
        """Testa formato de token inválido"""
        mock_jwt.validate_access_token.side_effect = Exception("Invalid token")

        response = client.get(
            "/auth/me",
            headers={"Authorization": "InvalidFormat"}
        )

        assert response.status_code in [401, 422, 500]

    @patch("src.main.jwt_handler")
    def test_invalid_bearer_token(self, mock_jwt):
        """Testa token Bearer inválido"""
        mock_jwt.validate_access_token.return_value = None

        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer token_invalido"}
        )

        assert response.status_code == 401