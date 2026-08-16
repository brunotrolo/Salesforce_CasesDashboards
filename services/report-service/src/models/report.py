from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """Types of reports supported."""
    SUMMARY = "summary"
    MATRIX = "matrix"
    TABULAR = "tabular"
    JOIN = "join"


class ReportStatus(str, Enum):
    """Report lifecycle status."""
    DRAFT = "draft"
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ReportMetadata(BaseModel):
    """Report metadata."""
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    version: str = "1.0"
    tags: List[str] = Field(default_factory=list)


class ReportSchedule(BaseModel):
    """Report execution schedule."""
    enabled: bool = False
    cron: Optional[str] = None  # e.g., "0 9 * * MON-FRI"
    timezone: str = "UTC"
    max_rows: int = 10000


class ReportFilter(BaseModel):
    """Report filter definition."""
    field: str
    operator: str  # "eq", "ne", "gt", "lt", "in", "contains"
    value: Any


class ReportAggregation(BaseModel):
    """Report aggregation definition."""
    field: str
    function: str  # "sum", "avg", "count", "min", "max"
    label: Optional[str] = None


class Report(BaseModel):
    """Complete report definition."""
    id: str
    name: str
    description: Optional[str] = None
    report_type: ReportType
    status: ReportStatus = ReportStatus.DRAFT

    # Data configuration
    object_type: str  # e.g., "Case", "Account", "Opportunity"
    fields: List[str]  # Fields to fetch from Salesforce
    filters: List[ReportFilter] = Field(default_factory=list)
    aggregations: List[ReportAggregation] = Field(default_factory=list)
    sort_by: Optional[str] = None
    limit: int = 1000

    # Schedule
    schedule: ReportSchedule = Field(default_factory=ReportSchedule)

    # Metadata
    metadata: ReportMetadata

    class Config:
        use_enum_values = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Salesforce storage."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Report":
        """Create from dictionary."""
        return cls(**data)

    def is_executable(self) -> bool:
        """Check if report can be executed."""
        return self.status in (ReportStatus.ACTIVE, ReportStatus.SCHEDULED)


class ReportExecutionResult(BaseModel):
    """Result of report execution."""
    report_id: str
    status: str  # "success", "failed", "partial"
    rows_returned: int
    execution_time_ms: int
    executed_at: datetime
    data: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    warning: Optional[str] = None


class ReportListItem(BaseModel):
    """Lightweight report item for listing."""
    id: str
    name: str
    report_type: ReportType
    status: ReportStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: str
