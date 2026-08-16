from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ReportType(str, Enum):
    SUMMARY = "SUMMARY"
    DETAILED = "DETAILED"
    MATRIX = "MATRIX"
    JOINED = "JOINED"

class ReportStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    DRAFT = "DRAFT"

class ReportMetadata(BaseModel):
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []

class ReportCreate(BaseModel):
    name: str
    report_type: ReportType
    object_type: str
    fields: List[str]
    metadata: Optional[ReportMetadata] = None
    status: ReportStatus = ReportStatus.DRAFT

class ReportUpdate(BaseModel):
    name: Optional[str] = None
    fields: Optional[List[str]] = None
    status: Optional[ReportStatus] = None
    metadata: Optional[ReportMetadata] = None

class Report(BaseModel):
    id: str
    name: str
    report_type: ReportType
    object_type: str
    fields: List[str]
    metadata: ReportMetadata
    status: ReportStatus
    salesforce_id: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

class ReportListResponse(BaseModel):
    items: List[Report]
    total: int
    offset: int
    limit: int
    success: bool = True

class ReportExecutionRequest(BaseModel):
    report_id: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None

class ReportExecutionResult(BaseModel):
    report_id: str
    status: str
    rows_returned: int
    execution_time_ms: int
    executed_at: str
    data: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None

class OAuthToken(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int
    expires_at: str

class OAuthAuthorizeResponse(BaseModel):
    authorization_url: str
    state: str
    expires_in: int

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str

class HealthCheck(BaseModel):
    service: str
    status: str
    timestamp: str
    version: str = "1.0"

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
