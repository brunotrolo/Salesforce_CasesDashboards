from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from src.config import settings
from src.models import TokenPayload, TokenType, UserRole

class JWTHandler:
    """Gerencia criação e validação de JWT tokens."""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_hours = settings.JWT_EXPIRATION_HOURS
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRATION_DAYS
    
    def create_access_token(
        self,
        user_id: str,
        role: UserRole,
        permissions: list = None,
    ) -> str:
        """
        Cria um novo access token.
        
        Args:
            user_id: ID do usuário
            role: Role do usuário
            permissions: Lista de permissões
            
        Returns:
            JWT access token
        """
        if permissions is None:
            permissions = []
        
        now = datetime.utcnow()
        expires = now + timedelta(hours=self.access_token_expire_hours)
        
        payload = {
            "sub": user_id,
            "exp": int(expires.timestamp()),
            "iat": int(now.timestamp()),
            "type": TokenType.ACCESS.value,
            "role": role.value,
            "permissions": permissions,
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Cria um novo refresh token.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            JWT refresh token
        """
        now = datetime.utcnow()
        expires = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "exp": int(expires.timestamp()),
            "iat": int(now.timestamp()),
            "type": TokenType.REFRESH.value,
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_token_pair(
        self,
        user_id: str,
        role: UserRole,
        permissions: list = None,
    ) -> Dict[str, str]:
        """
        Cria um par de tokens (access + refresh).
        
        Args:
            user_id: ID do usuário
            role: Role do usuário
            permissions: Lista de permissões
            
        Returns:
            Dict com access_token e refresh_token
        """
        access_token = self.create_access_token(user_id, role, permissions)
        refresh_token = self.create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_expire_hours * 3600,
        }
    
    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """
        Valida um JWT token.
        
        Args:
            token: JWT token para validar
            
        Returns:
            TokenPayload se válido, None se inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            token_data = TokenPayload(
                sub=payload.get("sub"),
                exp=payload.get("exp"),
                iat=payload.get("iat"),
                type=TokenType(payload.get("type")),
                role=UserRole(payload.get("role")),
                permissions=payload.get("permissions", []),
            )
            
            return token_data
        
        except JWTError:
            return None
    
    def validate_access_token(self, token: str) -> Optional[TokenPayload]:
        """
        Valida um access token especificamente.
        
        Args:
            token: JWT token
            
        Returns:
            TokenPayload se válido e é access token
        """
        token_data = self.validate_token(token)
        
        if token_data and token_data.type == TokenType.ACCESS:
            return token_data
        
        return None
    
    def validate_refresh_token(self, token: str) -> Optional[str]:
        """
        Valida um refresh token e retorna o user_id.
        
        Args:
            token: Refresh token
            
        Returns:
            User ID se válido
        """
        token_data = self.validate_token(token)
        
        if token_data and token_data.type == TokenType.REFRESH:
            return token_data.sub
        
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """Verifica se um token está expirado."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")
            
            if exp is None:
                return True
            
            return datetime.utcnow().timestamp() > exp
        
        except JWTError:
            return True
    
    def get_expiration_time(self, token: str) -> Optional[datetime]:
        """Retorna o tempo de expiração de um token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")
            
            if exp:
                return datetime.utcfromtimestamp(exp)
            
            return None
        
        except JWTError:
            return None
