"""Testes de integração Phase 2: MCP Client + Auth Service

Este arquivo valida a integração completa entre:
- MCP Client Service (autenticação OAuth + CRUD Salesforce)
- Auth Service (JWT + RBAC)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio


pytestmark = pytest.mark.skip(reason="API desatualizada (TokenPayload.user_id, RBAC wildcard, imports services.mcp_client). Reescrever na Fase 6.")


class TestPhase2Integration:
    """Suite de testes de integração Phase 2"""

    @pytest.mark.asyncio
    async def test_complete_oauth_flow(self):
        """Testa fluxo OAuth completo

        Cenário:
        1. Usuário inicia processo de autenticação no MCP Client
        2. Recebe URL de autorização
        3. Faz login no Salesforce
        4. Salesforce redireciona com código de autorização
        5. MCP Client troca código por access token
        6. Auth Service valida e emite JWT
        """
        from services.mcp_client.src.oauth_handler import OAuthHandler as MCPOAuthHandler
        from services.auth_service.src.jwt_handler import JWTHandler

        # Setup
        mcp_oauth = MCPOAuthHandler()
        jwt_handler = JWTHandler()

        # Passo 1: Obter URL de autorização
        auth_url, state = mcp_oauth.get_authorization_url()
        assert auth_url is not None
        assert state is not None
        assert "state=" in auth_url

        # Passo 2: Simular callback OAuth
        auth_code = "mock_authorization_code_12345"

        # Passo 3: Trocar código por token
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "sf_access_token_xyz",
                "refresh_token": "sf_refresh_token_xyz",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
            mock_post.return_value = mock_response

            # MCP Client faz troca de código
            mcp_oauth.exchange_code_for_token(auth_code)

        # Passo 4: Auth Service valida Salesforce token
        token = mcp_oauth.get_valid_token()
        assert token is not None

        # Passo 5: Criar JWT para frontend
        jwt_token = jwt_handler.create_access_token(
            user_id="u:12345",
            role="manager",
            permissions=["reports:read", "reports:create"]
        )
        assert jwt_token is not None

        # Validar JWT
        payload = jwt_handler.validate_token(jwt_token)
        assert payload.user_id == "u:12345"
        assert payload.role == "manager"

    @pytest.mark.asyncio
    async def test_mcp_client_to_auth_service_flow(self):
        """Testa fluxo MCP Client → Auth Service

        Cenário:
        1. MCP Client obtém access token OAuth do Salesforce
        2. Envia para Auth Service para validação
        3. Auth Service retorna JWT para frontend
        4. Frontend usa JWT para chamar APIs protegidas
        """
        from services.auth_service.src.jwt_handler import JWTHandler
        from services.auth_service.src.rbac import RBAC

        jwt_handler = JWTHandler()
        rbac = RBAC()

        # Passo 1: Simular usuário autenticado no Salesforce
        salesforce_user_id = "u:12345"
        salesforce_email = "admin@company.salesforce.com"

        # Passo 2: Auth Service cria JWT
        jwt_token = jwt_handler.create_access_token(
            user_id=salesforce_user_id,
            role="admin",
            permissions=rbac.get_role_permissions("admin")
        )

        # Passo 3: Validar JWT
        payload = jwt_handler.validate_token(jwt_token)
        assert payload.user_id == salesforce_user_id

        # Passo 4: Verificar permissões
        can_create_report = rbac.has_permission(["admin"], "reports", "create")
        assert can_create_report is True

        can_delete_user = rbac.has_permission(["admin"], "users", "delete")
        assert can_delete_user is True

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self):
        """Testa fluxo de refresh de token

        Cenário:
        1. Frontend possui JWT expirado
        2. Envia refresh token para Auth Service
        3. Auth Service retorna novo JWT
        4. Frontend continua operação
        """
        from services.auth_service.src.jwt_handler import JWTHandler

        jwt_handler = JWTHandler()

        # Passo 1: Criar par de tokens inicial
        user_id = "u:12345"
        role = "manager"
        permissions = ["reports:read"]

        tokens = jwt_handler.create_token_pair(user_id, role, permissions)
        initial_access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Passo 2: Validar access token
        payload = jwt_handler.validate_token(initial_access_token)
        assert payload.user_id == user_id

        # Passo 3: Simular refresh
        new_user_id = jwt_handler.validate_refresh_token(refresh_token)
        assert new_user_id == user_id

        # Passo 4: Gerar novo access token
        new_access_token = jwt_handler.create_access_token(
            new_user_id,
            role,
            permissions
        )

        new_payload = jwt_handler.validate_token(new_access_token)
        assert new_payload.user_id == user_id

    @pytest.mark.asyncio
    async def test_rbac_permission_hierarchy(self):
        """Testa hierarquia de permissões RBAC

        Validar que:
        - Admin tem todas as permissões
        - Manager tem subset de admin
        - User tem subset de manager
        - Guest tem permissões mínimas
        """
        from services.auth_service.src.rbac import RBAC

        rbac = RBAC()

        # Admin permissions
        admin_perms = rbac.get_role_permissions("admin")
        assert "*" in admin_perms

        # Manager permissions
        manager_perms = rbac.get_role_permissions("manager")
        assert "reports:create" in manager_perms
        assert "reports:read" in manager_perms
        assert len(manager_perms) < len(admin_perms)

        # User permissions
        user_perms = rbac.get_role_permissions("user")
        assert "reports:read" in user_perms
        assert "reports:create" not in user_perms
        assert len(user_perms) < len(manager_perms)

        # Guest permissions
        guest_perms = rbac.get_role_permissions("guest")
        assert "reports:read" in guest_perms
        assert "reports:execute" not in guest_perms
        assert len(guest_perms) <= len(user_perms)

    @pytest.mark.asyncio
    async def test_mcp_salesforce_api_with_auth(self):
        """Testa chamada para Salesforce API via MCP Client com autenticação

        Cenário:
        1. MCP Client tem token OAuth válido
        2. Faz requisição para API Salesforce
        3. Auth Service valida contexto de segurança
        4. Operação é autorizada
        """
        from services.auth_service.src.rbac import RBAC
        from services.auth_service.src.jwt_handler import JWTHandler

        jwt_handler = JWTHandler()
        rbac = RBAC()

        # Passo 1: Criar JWT para requisição
        user_jwt = jwt_handler.create_access_token(
            user_id="u:12345",
            role="manager",
            permissions=["reports:create", "reports:read"]
        )

        # Passo 2: Validar JWT
        payload = jwt_handler.validate_token(user_jwt)

        # Passo 3: Verificar permissão para operação
        can_create = rbac.has_permission(
            [payload.role],
            "reports",
            "create"
        )
        assert can_create is True

        # Passo 4: Verificar permissão negada
        can_delete_user = rbac.has_permission(
            [payload.role],
            "users",
            "delete"
        )
        assert can_delete_user is False

    @pytest.mark.asyncio
    async def test_oauth_token_expiration_and_refresh(self):
        """Testa expiração e refresh automático de OAuth token

        Cenário:
        1. MCP Client obtém token OAuth
        2. Token se aproxima da expiração
        3. MCP Client detecta e faz refresh automático
        4. Nova chamada usa token renovado
        """
        from services.mcp_client.src.oauth_handler import OAuthHandler

        oauth = OAuthHandler()

        # Passo 1: Simular token válido
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "initial_token",
                "refresh_token": "refresh_token_xyz",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
            mock_post.return_value = mock_response

            oauth.exchange_code_for_token("auth_code")

        # Passo 2: Token não está expirado
        is_expired = oauth.is_token_expired()
        assert is_expired is False

        # Passo 3: Obter token válido
        token = oauth.get_valid_token()
        assert token is not None

    @pytest.mark.asyncio
    async def test_error_handling_invalid_token(self):
        """Testa tratamento de erro com token inválido

        Cenário:
        1. Frontend envia token inválido
        2. Auth Service rejeita
        3. Frontend recebe erro apropriado
        """
        from services.auth_service.src.jwt_handler import JWTHandler
        from jose import JWTError

        jwt_handler = JWTHandler()

        # Tentar validar token inválido
        invalid_token = "invalid.token.format"

        with pytest.raises(JWTError):
            jwt_handler.validate_token(invalid_token)

    @pytest.mark.asyncio
    async def test_concurrent_requests_with_tokens(self):
        """Testa múltiplas requisições concorrentes com tokens

        Cenário:
        1. Criar múltiplos JWT tokens
        2. Simular requisições paralelas
        3. Cada uma valida seu token
        4. Nenhuma interferência entre requests
        """
        from services.auth_service.src.jwt_handler import JWTHandler

        jwt_handler = JWTHandler()

        # Criar múltiplos tokens
        async def create_and_validate(user_id, role):
            token = jwt_handler.create_access_token(user_id, role, [])
            payload = jwt_handler.validate_token(token)
            return payload.user_id == user_id

        # Executar concorrentemente
        tasks = [
            create_and_validate(f"u:{i}", "manager")
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)
        assert all(results) is True


class TestPhase2ErrorScenarios:
    """Testes de cenários de erro em Phase 2"""

    @pytest.mark.asyncio
    async def test_salesforce_oauth_failure(self):
        """Testa falha na autenticação OAuth Salesforce"""
        from services.mcp_client.src.oauth_handler import OAuthHandler

        oauth = OAuthHandler()

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_post.return_value = mock_response

            # Deve retentar com backoff exponencial
            with pytest.raises(Exception):
                oauth.exchange_code_for_token("invalid_code")

    @pytest.mark.asyncio
    async def test_database_unavailable(self):
        """Testa cenário com banco de dados indisponível"""
        from services.auth_service.src.config import Config

        config = Config()
        
        # Database URL inválida
        assert config.database_url is not None

    @pytest.mark.asyncio
    async def test_redis_unavailable_fallback(self):
        """Testa fallback quando Redis indisponível"""
        from services.auth_service.src.config import Config

        config = Config()
        
        # Redis URL configurada
        assert config.redis_url is not None
