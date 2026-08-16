import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.report_validator import ReportValidator, ValidationResult
from src.models.report import (
    Report, ReportType, ReportMetadata, ReportFilter,
    ReportAggregation, ReportSchedule
)


@pytest.fixture
def valid_report():
    """Create a valid report for testing."""
    return Report(
        id="report:valid",
        name="Valid Report",
        report_type=ReportType.SUMMARY,
        object_type="Case",
        fields=["Id", "Status", "Priority"],
        metadata=ReportMetadata(
            created_by="u:123",
            created_at=datetime.utcnow(),
        ),
    )


class TestReportValidator:
    def test_valid_report(self, valid_report):
        """Test validation passes for valid report."""
        result = ReportValidator.validate(valid_report)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_report_name(self):
        """Test validation fails with empty name."""
        report = Report(
            id="report:test",
            name="",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any(e.field == "name" for e in result.errors)

    def test_report_name_too_long(self):
        """Test validation fails with very long name."""
        report = Report(
            id="report:test",
            name="x" * 300,
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("name" in e.field.lower() for e in result.errors)

    def test_missing_report_id(self):
        """Test validation fails with empty ID."""
        report = Report(
            id="",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any(e.field == "id" for e in result.errors)

    def test_no_fields(self):
        """Test validation fails with no fields."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=[],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any(e.field == "fields" for e in result.errors)

    def test_too_many_fields(self):
        """Test validation fails with too many fields."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=[f"field_{i}" for i in range(150)],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("fields" in e.field.lower() for e in result.errors)

    def test_invalid_object_type(self):
        """Test validation fails with invalid object."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="InvalidObject",
            fields=["Id"],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("object_type" in e.field.lower() for e in result.errors)

    def test_invalid_filter_field(self):
        """Test validation fails with invalid filter field."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            filters=[
                ReportFilter(field="", operator="eq", value="test")
            ],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("filter" in e.field.lower() for e in result.errors)

    def test_invalid_filter_operator(self):
        """Test validation fails with invalid operator."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            filters=[
                ReportFilter(field="Status", operator="invalid_op", value="test")
            ],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("operator" in e.field.lower() for e in result.errors)

    def test_null_filter_value(self):
        """Test validation fails with null filter value."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            filters=[
                ReportFilter(field="Status", operator="eq", value=None)
            ],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False

    def test_null_filter_value_with_is_null_operator(self, valid_report):
        """Test validation passes with null value for is_null operator."""
        valid_report.filters = [
            ReportFilter(field="Status", operator="is_null", value=None)
        ]

        result = ReportValidator.validate(valid_report)

        assert result.is_valid is True

    def test_invalid_aggregation_function(self):
        """Test validation fails with invalid aggregation function."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            aggregations=[
                ReportAggregation(field="Amount", function="invalid_func")
            ],
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("function" in e.field.lower() for e in result.errors)

    def test_schedule_without_cron(self):
        """Test validation fails when schedule enabled without CRON."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            schedule=ReportSchedule(enabled=True, cron=None),
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("cron" in e.field.lower() for e in result.errors)

    def test_invalid_max_rows(self):
        """Test validation fails with invalid max_rows."""
        report = Report(
            id="report:test",
            name="Test Report",
            report_type=ReportType.SUMMARY,
            object_type="Case",
            fields=["Id"],
            schedule=ReportSchedule(enabled=True, cron="0 9 * * *", max_rows=0),
            metadata=ReportMetadata(
                created_by="u:123",
                created_at=datetime.utcnow(),
            ),
        )

        result = ReportValidator.validate(report)

        assert result.is_valid is False
        assert any("max_rows" in e.field.lower() for e in result.errors)

    def test_valid_field_names(self):
        """Test valid field name checking."""
        assert ReportValidator._is_valid_field_name("Id") is True
        assert ReportValidator._is_valid_field_name("CreatedDate") is True
        assert ReportValidator._is_valid_field_name("Owner.Name") is True
        assert ReportValidator._is_valid_field_name("Account.BillingCity") is True

    def test_invalid_field_names(self):
        """Test invalid field name checking."""
        assert ReportValidator._is_valid_field_name("") is False
        assert ReportValidator._is_valid_field_name("123Invalid") is False
        assert ReportValidator._is_valid_field_name("Field-Name") is False

    def test_suggest_fixes(self, valid_report):
        """Test getting fix suggestions."""
        valid_report.fields = []
        valid_report.limit = 500000

        suggestions = ReportValidator.suggest_fixes(valid_report)

        assert len(suggestions) > 0
        assert any("field" in s.lower() for s in suggestions)
        assert any("performance" in s.lower() for s in suggestions)

    def test_validation_result_bool(self):
        """Test ValidationResult bool conversion."""
        valid_result = ValidationResult(is_valid=True, errors=[])
        invalid_result = ValidationResult(is_valid=False, errors=[])

        assert bool(valid_result) is True
        assert bool(invalid_result) is False

    def test_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult(is_valid=True, errors=[])
        result.add_error("field", "Error message", "ERROR_CODE")

        assert len(result.errors) == 1
        assert result.errors[0].field == "field"
        assert result.errors[0].code == "ERROR_CODE"
