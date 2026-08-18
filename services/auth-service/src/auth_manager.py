"""
Auth Manager - Gerenciador centralizado de autenticação.
"""

from datetime import timedelta
from typing import Optional, Tuple
import hashlib
import secrets
import logging

from .jwt_handler import JWTHandler, TokenPayload
from .rbac import RBAC

logger = logging.getLogger(__name__)


class AuthManager:
    """Gerenciador centralizado de autenticação."""

    def __init__(self, jwt_handler: JWTHandler = None):
        """
        Inicializar manager.
        
        Args:
            jwt_handler: Handler de JWT tokens
        """
        self.jwt_handler = jwt_handler or JWTHandler()
        self.sessions: dict = {}  # session_id -> user_data

    def login(
        self,
        user_id: str,
        email: str,
        roles: list = None
    ) -> Tuple[str, str]:
        """
        Fazer login e retornar tokens.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            roles: Lista de roles
            
        Returns:
            Tuple de (access_token, refresh_token)
        """
        roles = roles or ["viewer"]
        
        # Criar tokens
        access_token = self.jwt_handler.create_access_token(
            user_id=user_id,
            email=email,
            roles=roles,
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = self.jwt_handler.create_refresh_token(
            user_id=user_id,
            email=email,
            expires_delta=timedelta(days=7)
        )
        
        # Criar sessão
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user_id,
            "email": email,
            "roles": roles,
            "refresh_token": refresh_token
        }
        
        logger.info(
            "User logged in",
            extra={"user_id": user_id, "session_id": session_id}
        )
        
        return access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Renovar access token usando refresh token.
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            Novo access token ou None se inválido
        """
        try:
            payload = self.jwt_handler.verify_token(refresh_token)
            
            # Criar novo access token
            new_access_token = self.jwt_handler.create_access_token(
                user_id=payload.sub,
                email=payload.email,
                roles=payload.roles,
                expires_delta=timedelta(hours=1)
            )
            
            logger.info(
                "Access token refreshed",
                extra={"user_id": payload.sub}
            )
            
            return new_access_token
            
        except Exception as e:
            logger.warning(
                "Token refresh failed",
                extra={"error": str(e)}
            )
            return None

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """
        Verificar token de acesso.
        
        Args:
            token: Access token
            
        Returns:
            TokenPayload se válido, None se inválido
        """
        try:
            payload = self.jwt_handler.verify_token(token)
            return payload
        except Exception as e:
            logger.warning("Token verification failed", extra={"error": str(e)})
            return None

    def logout(self, session_id: str) -> bool:
        """
        Fazer logout.
        
        Args:
            session_id: Session ID
            
        Returns:
            True se logout bem-sucedido
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info("User logged out", extra={"session_id": session_id})
            return True
        return False

    def check_permission(self, roles: list, permission: str) -> bool:
        """
        Verificar permissão.
        
        Args:
            roles: Roles do usuário
            permission: Permissão a verificar
            
        Returns:
            True se tem permissão
        """
        return RBAC.has_permission(roles, permission)
