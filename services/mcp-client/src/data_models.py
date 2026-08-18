"""
Data models for Salesforce reports.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ReportMetadata(BaseModel):
    """Metadados do relatório."""
    type: str = "report"
    version: str = "1.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReportConfig(BaseModel):
    """Configuração de um relatório Salesforce."""
    id: str
    name: str
    description: Optional[str] = None
    report_type: str
    data_source: str
    fields: List[str] = []
    filters: Dict[str, Any] = {}
    aggregations: Dict[str, Any] = {}
    metadata: ReportMetadata = Field(default_factory=ReportMetadata)

    def to_json(self) -> str:
        """Converter para JSON string."""
        import json
        return json.dumps(self.model_dump(), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "ReportConfig":
        """Criar a partir de JSON string."""
        import json
        return cls(**json.loads(json_str))


class SalesforceResponse(BaseModel):
    """Resposta padrão do Salesforce."""
    success: bool
    id: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class OAuth2Credentials(BaseModel):
    """Credenciais OAuth2 para Salesforce."""
    client_id: str
    client_secret: str
    refresh_token: str
    access_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    instance_url: Optional[str] = None
