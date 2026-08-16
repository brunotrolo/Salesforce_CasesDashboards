import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.report_manager import ReportManager
from src.models.report import (
    Report, ReportStatus, ReportType, ReportMetadata,
    ReportFilter, ReportAggregation
)


@pytest.fixture
def manager():
    """Create a report manager instance."""
    return ReportManager()


@pytest.fixture
def sample_report():
    """Create a sample report for testing."""
    return Report(
        id="report:123",
        name="Sales Report",
        description="Monthly sales metrics",
        report_type=ReportType.SUMMARY,
        object_type="Opportunity",
        fields=["Id", "Name", "Amount", "StageName"],
        filters=[
            ReportFilter(
                field="StageName",
                operator="eq",
                value="Closed Won"
            )
        ],
        aggregations=[
            ReportAggregation(
                field="Amount",
                function="sum",
                label="Total Amount"
            )
        ],
        metadata=ReportMetadata(
            created_by="u:123",
            created_at=datetime.utcnow(),
            version="1.0",
        ),
    )


@pytest.mark.asyncio
class TestReportManager:
    async def test_create_report(self, manager, sample_report):
        """Test creating a report."""
        result = await manager.create_report(sample_report, "u:123")

        assert result["success"] is True
        assert result["report_id"] == "report:123"
        assert result["status"] == ReportStatus.DRAFT.value
        assert "report:123" in manager.reports

    async def test_create_report_with_validation_error(self, manager):
        """Test creating report with invalid configuration."""
        invalid_report = Report(
            id="report:456",
            name="",  # Empty name
            report_type=ReportType.SUMMARY,
            object_type="InvalidObject",
            fields=[],  # No fields
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = await manager.create_report(invalid_report, "u:123")

        assert result["success"] is False
        assert "validation_errors" in result

    async def test_get_report(self, manager, sample_report):
        """Test retrieving a report."""
        await manager.create_report(sample_report, "u:123")
        retrieved = await manager.get_report("report:123")

        assert retrieved is not None
        assert retrieved.name == "Sales Report"

    async def test_get_report_not_found(self, manager):
        """Test retrieving non-existent report."""
        result = await manager.get_report("non:existent")
        assert result is None

    async def test_update_report(self, manager, sample_report):
        """Test updating a report."""
        await manager.create_report(sample_report, "u:123")

        updates = {"name": "Updated Sales Report"}
        result = await manager.update_report("report:123", updates, "u:456")

        assert result["success"] is True
        assert manager.reports["report:123"].name == "Updated Sales Report"
        assert manager.reports["report:123"].metadata.updated_by == "u:456"

    async def test_update_nonexistent_report(self, manager):
        """Test updating non-existent report."""
        result = await manager.update_report("non:existent", {"name": "New"}, "u:123")
        assert result["success"] is False

    async def test_delete_report(self, manager, sample_report):
        """Test deleting (archiving) a report."""
        await manager.create_report(sample_report, "u:123")
        result = await manager.delete_report("report:123")

        assert result["success"] is True
        assert manager.reports["report:123"].status == ReportStatus.ARCHIVED

    async def test_delete_nonexistent_report(self, manager):
        """Test deleting non-existent report."""
        result = await manager.delete_report("non:existent")
        assert result["success"] is False

    async def test_list_reports(self, manager, sample_report):
        """Test listing reports."""
        await manager.create_report(sample_report, "u:123")

        result = await manager.list_reports()

        assert result["success"] is True
        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "Sales Report"

    async def test_list_reports_with_pagination(self, manager, sample_report):
        """Test list pagination."""
        for i in range(5):
            report = Report(
                id=f"report:{i}",
                name=f"Report {i}",
                report_type=ReportType.SUMMARY,
                object_type="Case",
                fields=["Id", "Status"],
                metadata=ReportMetadata(
                    created_by="u:123",
                    created_at=datetime.utcnow(),
                ),
            )
            await manager.create_report(report, "u:123")

        result = await manager.list_reports(limit=2, offset=0)

        assert result["total"] == 5
        assert len(result["items"]) == 2
        assert result["offset"] == 0

    async def test_list_reports_by_status(self, manager, sample_report):
        """Test filtering reports by status."""
        await manager.create_report(sample_report, "u:123")
        await manager.activate_report("report:123", "u:123")

        draft_result = await manager.list_reports(status=ReportStatus.DRAFT)
        active_result = await manager.list_reports(status=ReportStatus.ACTIVE)

        assert draft_result["total"] == 0
        assert active_result["total"] == 1

    async def test_execute_report(self, manager, sample_report):
        """Test executing a report."""
        await manager.create_report(sample_report, "u:123")
        await manager.activate_report("report:123", "u:123")

        result = await manager.execute_report("report:123")

        assert result.status == "success"
        assert result.rows_returned > 0
        assert result.execution_time_ms >= 0
        assert len(result.data) > 0

    async def test_execute_draft_report(self, manager, sample_report):
        """Test executing draft report fails."""
        await manager.create_report(sample_report, "u:123")

        result = await manager.execute_report("report:123")

        assert result.status == "failed"
        assert "cannot execute" in result.error.lower()

    async def test_execute_nonexistent_report(self, manager):
        """Test executing non-existent report."""
        result = await manager.execute_report("non:existent")

        assert result.status == "failed"
        assert "not found" in result.error.lower()

    async def test_activate_report(self, manager, sample_report):
        """Test activating a report."""
        await manager.create_report(sample_report, "u:123")
        result = await manager.activate_report("report:123", "u:456")

        assert result["success"] is True
        assert manager.reports["report:123"].status == ReportStatus.ACTIVE

    async def test_activate_active_report_fails(self, manager, sample_report):
        """Test activating already active report fails."""
        await manager.create_report(sample_report, "u:123")
        await manager.activate_report("report:123", "u:123")

        result = await manager.activate_report("report:123", "u:456")

        assert result["success"] is False

    async def test_schedule_report(self, manager, sample_report):
        """Test scheduling a report."""
        await manager.create_report(sample_report, "u:123")

        result = await manager.schedule_report(
            "report:123",
            "0 9 * * MON-FRI",
            "u:456"
        )

        assert result["success"] is True
        assert manager.reports["report:123"].status == ReportStatus.SCHEDULED
        assert manager.reports["report:123"].schedule.cron == "0 9 * * MON-FRI"

    async def test_pause_report(self, manager, sample_report):
        """Test pausing a report."""
        await manager.create_report(sample_report, "u:123")
        await manager.schedule_report("report:123", "0 9 * * *", "u:123")

        result = await manager.pause_report("report:123", "u:456")

        assert result["success"] is True
        assert manager.reports["report:123"].status == ReportStatus.PAUSED
        assert manager.reports["report:123"].schedule.enabled is False

    async def test_cache_invalidation_on_update(self, manager, sample_report):
        """Test cache is invalidated on report update."""
        await manager.create_report(sample_report, "u:123")
        await manager.activate_report("report:123", "u:123")

        # Execute to cache
        await manager.execute_report("report:123")
        assert manager.cache.get_cached_result("report:123") is not None

        # Update should invalidate
        await manager.update_report("report:123", {"name": "New Name"}, "u:123")
        assert manager.cache.get_cached_result("report:123") is None

    async def test_validate_report(self, manager, sample_report):
        """Test report validation."""
        validation = await manager.validate_report(sample_report)

        assert validation.is_valid is True
        assert len(validation.errors) == 0

    async def test_get_cache_stats(self, manager):
        """Test getting cache statistics."""
        stats = manager.get_cache_stats()

        assert "total_entries" in stats
        assert "active_entries" in stats
        assert "expired_entries" in stats
        assert "ttl_minutes" in stats
