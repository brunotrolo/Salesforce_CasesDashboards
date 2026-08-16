import pytest
from datetime import datetime, timedelta
from src.oauth_handler import OAuthHandler
from src.models import OAuthToken

class TestOAuthHandler:
    
    def test_get_authorization_url(self, oauth_handler):
        """Testa geração de URL de autorização."""
        auth_url, state = oauth_handler.get_authorization_url()
        
        assert "client_id=" in auth_url
        assert "redirect_uri=" in auth_url
        assert "response_type=code" in auth_url
        assert len(state) > 0
    
    def test_is_token_expired_no_token(self, oauth_handler):
        """Testa se token expirado quando não há token."""
        assert oauth_handler.is_token_expired() is True
    
    def test_is_token_expired_valid_token(self, oauth_handler, mock_token):
        """Testa se token não está expirado."""
        oauth_handler.set_token(mock_token)
        assert oauth_handler.is_token_expired() is False
    
    def test_is_token_expired_expired_token(self, oauth_handler):
        """Testa se token está expirado."""
        expired_token = OAuthToken(
            access_token="test",
            refresh_token="test",
            token_type="Bearer",
            expires_in=1,
            expires_at=(datetime.utcnow() - timedelta(hours=1)).isoformat(),
        )
        oauth_handler.set_token(expired_token)
        assert oauth_handler.is_token_expired() is True
    
    def test_set_token(self, oauth_handler, mock_token):
        """Testa configuração manual de token."""
        oauth_handler.set_token(mock_token)
        assert oauth_handler.current_token == mock_token
    
    def test_get_valid_token_with_valid_token(self, oauth_handler, mock_token):
        """Testa obtenção de token válido."""
        oauth_handler.set_token(mock_token)
        token = oauth_handler.get_valid_token()
        assert token == mock_token.access_token
    
    def test_parse_token_response(self):
        """Testa parsing de resposta OAuth."""
        response = {
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        
        token = OAuthHandler._parse_token_response(response)
        
        assert token.access_token == "test_access"
        assert token.refresh_token == "test_refresh"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600
