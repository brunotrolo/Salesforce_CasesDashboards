import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models.report import (
    Report, ReportStatus, ReportExecutionResult, ReportListItem
)
from .report_validator import ReportValidator, ValidationResult
from .report_cache import ReportCache


class ReportManager:
    """Manages report lifecycle: CRUD, validation, execution, caching."""

    def __init__(self, cache: Optional[ReportCache] = None):
        self.cache = cache or ReportCache(ttl_minutes=60)
        self.reports: Dict[str, Report] = {}

    async def create_report(
        self,
        report: Report,
        user_id: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new report with validation."""
        validation = ReportValidator.validate(report)
        if not validation:
            return {
                "success": False,
                "error": "Validation failed",
                "validation_errors": [
                    {"field": e.field, "message": e.message}
                    for e in validation.errors
                ],
            }

        report.metadata.created_by = user_id
        report.metadata.created_at = datetime.utcnow()
        report.status = ReportStatus.DRAFT

        self.reports[report.id] = report

        return {
            "success": True,
            "report_id": report.id,
            "status": report.status.value,
            "created_at": report.metadata.created_at.isoformat(),
        }

    async def get_report(
        self,
        report_id: str,
        trace_id: Optional[str] = None,
    ) -> Optional[Report]:
        """Retrieve a report by ID."""
        return self.reports.get(report_id)

    async def update_report(
        self,
        report_id: str,
        updates: Dict[str, Any],
        user_id: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing report."""
        report = self.reports.get(report_id)
        if not report:
            return {"success": False, "error": "Report not found"}

        # Apply updates
        for key, value in updates.items():
            if hasattr(report, key) and key not in ["id", "metadata"]:
                setattr(report, key, value)

        # Update metadata
        report.metadata.updated_by = user_id
        report.metadata.updated_at = datetime.utcnow()

        # Re-validate
        validation = ReportValidator.validate(report)
        if not validation:
            return {
                "success": False,
                "error": "Validation failed after update",
                "validation_errors": [
                    {"field": e.field, "message": e.message}
                    for e in validation.errors
                ],
            }

        # Invalidate cache
        self.cache.invalidate_report(report_id)

        return {
            "success": True,
            "report_id": report_id,
            "updated_at": report.metadata.updated_at.isoformat(),
        }

    async def delete_report(
        self,
        report_id: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete a report (soft delete - archive)."""
        report = self.reports.get(report_id)
        if not report:
            return {"success": False, "error": "Report not found"}

        report.status = ReportStatus.ARCHIVED

        # Invalidate cache
        self.cache.invalidate_report(report_id)

        return {
            "success": True,
            "report_id": report_id,
            "status": ReportStatus.ARCHIVED.value,
        }

    async def list_reports(
        self,
        status: Optional[ReportStatus] = None,
        limit: int = 100,
        offset: int = 0,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List reports with optional filtering."""
        reports_list = list(self.reports.values())

        # Filter by status
        if status:
            reports_list = [r for r in reports_list if r.status == status]

        # Exclude archived unless specifically requested
        if status != ReportStatus.ARCHIVED:
            reports_list = [r for r in reports_list if r.status != ReportStatus.ARCHIVED]

        # Apply pagination
        total = len(reports_list)
        reports_list = reports_list[offset:offset + limit]

        items = [
            ReportListItem(
                id=r.id,
                name=r.name,
                report_type=r.report_type,
                status=r.status,
                created_at=r.metadata.created_at,
                updated_at=r.metadata.updated_at,
                created_by=r.metadata.created_by,
            )
            for r in reports_list
        ]

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [item.model_dump() for item in items],
        }

    async def execute_report(
        self,
        report_id: str,
        filters: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> ReportExecutionResult:
        """Execute a report and return results."""
        report = self.reports.get(report_id)
        if not report:
            return ReportExecutionResult(
                report_id=report_id,
                status="failed",
                rows_returned=0,
                execution_time_ms=0,
                executed_at=datetime.utcnow(),
                error="Report not found",
            )

        if not report.is_executable():
            return ReportExecutionResult(
                report_id=report_id,
                status="failed",
                rows_returned=0,
                execution_time_ms=0,
                executed_at=datetime.utcnow(),
                error=f"Report status is {report.status.value}, cannot execute",
            )

        # Check cache
        cached = self.cache.get_cached_result(report_id, filters)
        if cached:
            return cached

        # Simulate execution (in real implementation, call MCP Client)
        start_time = datetime.utcnow()
        await asyncio.sleep(0.1)  # Simulate work

        result = ReportExecutionResult(
            report_id=report_id,
            status="success",
            rows_returned=42,  # Simulated
            execution_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            executed_at=datetime.utcnow(),
            data=[
                {"id": f"rec_{i}", "name": f"Record {i}", "value": i * 100}
                for i in range(min(5, report.limit))
            ],
        )

        # Cache result
        self.cache.cache_result(report_id, result, filters)

        return result

    async def activate_report(
        self,
        report_id: str,
        user_id: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Activate a report for use."""
        report = self.reports.get(report_id)
        if not report:
            return {"success": False, "error": "Report not found"}

        if report.status != ReportStatus.DRAFT:
            return {
                "success": False,
                "error": f"Can only activate DRAFT reports, current status: {report.status.value}",
            }

        report.status = ReportStatus.ACTIVE
        report.metadata.updated_by = user_id
        report.metadata.updated_at = datetime.utcnow()

        return {
            "success": True,
            "report_id": report_id,
            "status": ReportStatus.ACTIVE.value,
        }

    async def schedule_report(
        self,
        report_id: str,
        cron: str,
        user_id: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a report for regular execution."""
        report = self.reports.get(report_id)
        if not report:
            return {"success": False, "error": "Report not found"}

        report.schedule.enabled = True
        report.schedule.cron = cron
        report.status = ReportStatus.SCHEDULED
        report.metadata.updated_by = user_id
        report.metadata.updated_at = datetime.utcnow()

        return {
            "success": True,
            "report_id": report_id,
            "status": ReportStatus.SCHEDULED.value,
            "cron": cron,
        }

    async def pause_report(
        self,
        report_id: str,
        user_id: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pause a scheduled report."""
        report = self.reports.get(report_id)
        if not report:
            return {"success": False, "error": "Report not found"}

        report.schedule.enabled = False
        report.status = ReportStatus.PAUSED
        report.metadata.updated_by = user_id
        report.metadata.updated_at = datetime.utcnow()

        return {
            "success": True,
            "report_id": report_id,
            "status": ReportStatus.PAUSED.value,
        }

    async def validate_report(self, report: Report) -> ValidationResult:
        """Validate a report configuration."""
        return ReportValidator.validate(report)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.stats()

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self.cache.clear()
