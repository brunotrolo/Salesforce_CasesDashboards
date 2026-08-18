"""Security tests for API Gateway: auth bypass, mass assignment, injection."""

import pytest


class TestAuthBypass:
    def test_invalid_token_rejected(self, client):
        """Token forjado/inválido é rejeitado."""
        response = client.get(
            "/api/reports",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_empty_bearer_rejected(self, client):
        response = client.get(
            "/api/reports",
            headers={"Authorization": "Bearer "},
        )
        assert response.status_code == 401

    def test_malformed_auth_header_rejected(self, client):
        response = client.get(
            "/api/reports",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert response.status_code == 401

    def test_all_report_endpoints_require_auth(self, client):
        """Todos os endpoints de report exigem autenticação."""
        assert client.get("/api/reports/1").status_code == 401
        assert client.put("/api/reports/1", json={"name": "x"}).status_code == 401
        assert client.delete("/api/reports/1").status_code == 401
        assert client.post("/api/reports/1/execute").status_code == 401
        assert client.post("/api/reports/1/activate").status_code == 401
        assert client.post("/api/reports/1/schedule").status_code == 401
        assert client.post("/api/reports/1/pause").status_code == 401


class TestMassAssignment:
    def test_extra_fields_ignored_on_create(self, client, auth_headers):
        """Campos privilegiados enviados no payload são ignorados.

        created_by / owner_id / is_admin não devem sobrescrever o usuário
        autenticado nem conceder privilégios.
        """
        report_data = {
            "name": "Mass Assignment Test",
            "object_type": "Case",
            "report_type": "summary",
            "fields": ["Id", "Subject"],
            "created_by": "u:attacker",
            "owner_id": "u:attacker",
            "is_admin": True,
        }

        response = client.post(
            "/api/reports",
            json=report_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 400]
        if response.status_code in [200, 201]:
            data = response.json()
            body = str(data).lower()
            assert "attacker" not in body


class TestInjection:
    def test_soql_injection_in_fields_rejected(self, client, auth_headers):
        """Fields com injeção SOQL são rejeitados (400) ou sanitizados."""
        report_data = {
            "name": "Injection Test",
            "object_type": "Case",
            "report_type": "summary",
            "fields": ["Id", "Status FROM Case; DROP TABLE Case;--"],
        }

        response = client.post(
            "/api/reports",
            json=report_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 400, 422]
        if response.status_code in [200, 201]:
            body = str(response.json()).lower()
            assert "drop table" not in body

    def test_object_type_injection_rejected(self, client, auth_headers):
        """object_type com payload malicioso é rejeitado."""
        report_data = {
            "name": "Injection Test",
            "object_type": "Case; DELETE FROM Case",
            "report_type": "summary",
            "fields": ["Id"],
        }

        response = client.post(
            "/api/reports",
            json=report_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 400, 422]
        if response.status_code in [200, 201]:
            body = str(response.json()).lower()
            assert "delete from" not in body


class TestLoginBruteForce:
    def test_unknown_user_and_password_rejected(self, client):
        """Login com credenciais inventadas não retorna token."""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "bruteforce"},
        )
        assert response.status_code == 401
        assert "access_token" not in response.json()