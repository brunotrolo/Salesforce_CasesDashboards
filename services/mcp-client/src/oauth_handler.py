import httpx
import secrets
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from src.config import settings
from src.logger import log
from src.models import OAuthToken
import json

class OAuthHandler:
    """Gerencia o fluxo OAuth 2.0 com Salesforce."""
    
    def __init__(self):
        self.client_id = settings.SF_CLIENT_ID
        self.client_secret = settings.SF_CLIENT_SECRET
        self.redirect_uri = settings.SF_REDIRECT_URI
        self.instance_url = settings.SF_INSTANCE_URL
        self.current_token: Optional[OAuthToken] = None
        self.retry_attempts = settings.OAUTH_RETRY_ATTEMPTS
        self.retry_delay = settings.OAUTH_RETRY_DELAY
    
    def get_authorization_url(self) -> Tuple[str, str]:
        """
        Gera URL de autorização e state para iniciar OAuth flow.
        
        Returns:
            Tupla (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"{self.instance_url}/services/oauth2/authorize?"
            f"client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&state={state}"
            f"&scope=api%20refresh_token%20web"
        )
        
        log.info("URL de autorização gerada", state=state[:8])
        return auth_url, state
    
    def exchange_code_for_token(self, code: str) -> OAuthToken:
        """
        Troca authorization code por access token.
        
        Args:
            code: Authorization code do callback
            
        Returns:
            OAuthToken com access_token e refresh_token
        """
        token_url = f"{self.instance_url}/services/oauth2/token"
        
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        
        for attempt in range(self.retry_attempts):
            try:
                log.debug(f"Tentativa {attempt + 1} de troca de código por token")
                
                response = httpx.post(
                    token_url,
                    data=payload,
                    timeout=settings.OAUTH_TIMEOUT
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.current_token = self._parse_token_response(token_data)
                    log.info("Token obtido com sucesso")
                    return self.current_token
                
                elif response.status_code in [429, 503, 504]:
                    if attempt < self.retry_attempts - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        log.warning(
                            f"Erro {response.status_code}, aguardando {wait_time}s"
                        )
                        time.sleep(wait_time)
                        continue
                
                error_data = response.json()
                raise Exception(f"Erro OAuth: {error_data.get('error_description')}")
            
            except httpx.TimeoutException:
                log.warning(f"Timeout na tentativa {attempt + 1}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise
            
            except Exception as e:
                log.error("Erro ao trocar código por token", error=e)
                if attempt == self.retry_attempts - 1:
                    raise
                time.sleep(self.retry_delay * (2 ** attempt))
        
        raise Exception("Falha ao obter token após várias tentativas")
    
    def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """
        Renova access token usando refresh token.
        
        Args:
            refresh_token: Token de refresh
            
        Returns:
            OAuthToken com novo access_token
        """
        token_url = f"{self.instance_url}/services/oauth2/token"
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = httpx.post(
                token_url,
                data=payload,
                timeout=settings.OAUTH_TIMEOUT
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.current_token = self._parse_token_response(token_data)
                log.info("Token renovado com sucesso")
                return self.current_token
            
            error_data = response.json()
            raise Exception(f"Erro ao renovar token: {error_data}")
        
        except Exception as e:
            log.error("Falha ao renovar token", error=e)
            raise
    
    def is_token_expired(self) -> bool:
        """Verifica se o token atual está expirado."""
        if not self.current_token:
            return True
        
        # Renovar 5 minutos antes da expiração
        buffer_time = timedelta(minutes=5)
        expires_at = datetime.fromisoformat(self.current_token.expires_at)
        return datetime.utcnow() >= (expires_at - buffer_time)
    
    def get_valid_token(self) -> str:
        """
        Obtém um token válido, renovando se necessário.
        
        Returns:
            Access token válido
        """
        if not self.current_token:
            if settings.SF_REFRESH_TOKEN:
                self.refresh_access_token(settings.SF_REFRESH_TOKEN)
            else:
                raise Exception("Nenhum token disponível. Execute OAuth flow primeiro.")
        
        if self.is_token_expired():
            if self.current_token.refresh_token:
                self.refresh_access_token(self.current_token.refresh_token)
            else:
                raise Exception("Token expirado e sem refresh token disponível")
        
        return self.current_token.access_token
    
    def set_token(self, token: OAuthToken):
        """Define manualmente um token."""
        self.current_token = token
        log.info("Token definido manualmente")
    
    @staticmethod
    def _parse_token_response(data: Dict) -> OAuthToken:
        """Converte resposta OAuth em modelo OAuthToken."""
        expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
        
        return OAuthToken(
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 3600),
            expires_at=expires_at.isoformat(),
        )
