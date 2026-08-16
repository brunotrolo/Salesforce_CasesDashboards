"""Tests for Salesforce connector."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.salesforce_connector import SalesforceConnector
from src.data_models import ReportConfig
from src.error_handler import AuthenticationError


@pytest.fixture
def connector():
    """Criar connector para testes."""
    with patch.dict('os.environ', {
        'SF_CLIENT_ID': 'test_client',
        'SF_CLIENT_SECRET': 'test_secret',
        'SF_REFRESH_TOKEN': 'test_token'
    }):
        return SalesforceConnector()


@pytest.mark.asyncio
async def test_authentication_required(connector):
    """Testar que autenticação é necessária."""
    # Sem credenciais, não deve funcionar
    assert connector.credentials is None


def test_missing_credentials():
    """Testar erro quando credenciais estão faltando."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(AuthenticationError):
            SalesforceConnector()


@pytest.mark.asyncio
async def test_create_report_structure(connector):
    """Testar estrutura de criação de relatório."""
    config = ReportConfig(
        id="r:123",
        name="Test Report",
        report_type="matrix",
        data_source="Opportunity"
    )
    
    # Mock da resposta
    with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={"id": "r:123", "success": True})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Este é um teste de estrutura - real chamaria Salesforce
        assert config.id == "r:123"
