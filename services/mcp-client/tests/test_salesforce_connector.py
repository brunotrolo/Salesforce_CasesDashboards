"""Tests for Salesforce connector."""

import pytest
from unittest.mock import Mock, patch
from src.salesforce_connector import SalesforceConnector
from src.data_models import ReportConfig
from src.error_handler import AuthenticationError


@pytest.fixture
def connector():
    """Criar connector para testes."""
    oauth = Mock()
    oauth.get_valid_token.return_value = "test_token"
    return SalesforceConnector(oauth_handler=oauth)


def test_authentication_required():
    """Testar que autenticação é necessária para chamadas."""
    connector = SalesforceConnector(oauth_handler=Mock())
    assert connector.instance_url is not None


def test_missing_credentials():
    """Testar erro quando credenciais estão faltando."""
    oauth = Mock()
    oauth.get_valid_token.side_effect = AuthenticationError("Credenciais ausentes")
    connector = SalesforceConnector(oauth_handler=oauth)

    with pytest.raises(AuthenticationError):
        connector._get_headers()


def test_create_report_structure():
    """Testar estrutura de criação de relatório."""
    config = ReportConfig(
        id="r:123",
        name="Test Report",
        report_type="matrix",
        data_source="Opportunity"
    )

    assert config.id == "r:123"
    assert config.name == "Test Report"


def test_get_headers_with_token():
    """Testar headers com token válido."""
    connector = SalesforceConnector(oauth_handler=Mock())
    headers = connector._get_headers()

    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")