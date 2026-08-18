"""Shared data models used across multiple services."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ReportMetadata(BaseModel):
    """Metadados do relatório (schema unificado)."""
    type: str = "report"
    version: str = "1.0"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
