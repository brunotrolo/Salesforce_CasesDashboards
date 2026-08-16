"""
MCP Salesforce Client
Integração com Salesforce via MCP para operações CRUD de relatórios.
"""

from .salesforce_connector import SalesforceConnector
from .data_models import SalesforceResponse

__version__ = "0.1.0"

__all__ = [
    "SalesforceConnector",
    "SalesforceResponse",
]
