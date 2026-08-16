"""Tests for data models."""

import pytest
import json
from datetime import datetime
from src.data_models import ReportConfig, ReportMetadata, OAuth2Credentials


def test_report_config_creation():
    """Testar criação de ReportConfig."""
    config = ReportConfig(
        id="r:123",
        name="Sales Report",
        description="Monthly sales data",
        report_type="matrix",
        data_source="Opportunity",
        fields=["Id", "Name", "Amount"],
        filters={"StageName": "Closed Won"}
    )
    
    assert config.id == "r:123"
    assert config.name == "Sales Report"
    assert len(config.fields) == 3


def test_report_config_json_conversion():
    """Testar conversão para JSON."""
    config = ReportConfig(
        id="r:123",
        name="Sales Report",
        report_type="matrix",
        data_source="Opportunity"
    )
    
    json_str = config.to_json()
    assert isinstance(json_str, str)
    
    # Converter de volta
    parsed = json.loads(json_str)
    assert parsed["id"] == "r:123"
    assert parsed["name"] == "Sales Report"


def test_oauth2_credentials():
    """Testar credenciais OAuth2."""
    creds = OAuth2Credentials(
        client_id="client123",
        client_secret="secret456",
        refresh_token="refresh789"
    )
    
    assert creds.client_id == "client123"
    assert creds.access_token is None  # Até que se autentique
