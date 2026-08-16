"""
JWT token generation and validation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from jose import JWTError, jwt
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class TokenPayload(BaseModel):
    """Payload do JWT token."""
    sub: str  # user_id
    email: str
    roles: list = []
    exp: datetime
    iat: datetime


class JWTHandler:
    """Gerenciador de JWT tokens."""

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
        Inicializar handler.
        
        Args:
            secret_key: Chave secreta para assinar tokens
            algorithm: Algoritmo de assinatura (HS256, RS256, etc)
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "change_me")
        self.algorithm = algorithm

    def create_access_token(
        self,
        user_id: str,
        email: str,
        roles: list = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Criar access token.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            roles: Lista de roles
            expires_delta: Tempo até expiração
            
        Returns:
            JWT token string
        """
        roles = roles or []
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=1)

        payload = {
            "sub": user_id,
            "email": email,
            "roles": roles,
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.info(
            "Access token created",
            extra={"user_id": user_id, "expires_at": expire}
        )

        return encoded_jwt

    def create_refresh_token(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Criar refresh token.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            expires_delta: Tempo até expiração (default: 7 dias)
            
        Returns:
            JWT refresh token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)

        payload = {
            "sub": user_id,
            "email": email,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.info(
            "Refresh token created",
            extra={"user_id": user_id, "expires_at": expire}
        )

        return encoded_jwt

    def verify_token(self, token: str) -> TokenPayload:
        """
        Verificar e decodificar token.
        
        Args:
            token: JWT token
            
        Returns:
            TokenPayload com dados do usuário
            
        Raises:
            JWTError: Se token é inválido ou expirou
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            user_id = payload.get("sub")
            email = payload.get("email")
            roles = payload.get("roles", [])

            if not user_id:
                raise JWTError("Token payload invalid")

            return TokenPayload(
                sub=user_id,
                email=email,
                roles=roles,
                exp=datetime.fromtimestamp(payload.get("exp")),
                iat=datetime.fromtimestamp(payload.get("iat"))
            )

        except JWTError as e:
            logger.warning(
                "Token verification failed",
                extra={"error": str(e)}
            )
            raise
